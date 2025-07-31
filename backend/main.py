from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent_graph import build_triad_agent
import uuid
import os
from fastapi import Query
from prompts import summary_prompt
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from tts_client import tts_client

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
print(MODEL_NAME)
# Get root path for proxy deployment
ROOT_PATH = os.getenv("ROOT_PATH", "")

# --- Setup Gemini ---
llm = genai.Client(api_key=GEMINI_API_KEY)

# Request models
class TextTriageRequest(BaseModel):
    user_input: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class TTSRequest(BaseModel):
    text: str
    voice: str = "female"

app = FastAPI(root_path=ROOT_PATH)

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Build the agent once
triage_graph = build_triad_agent()

# In-memory session storage
sessions = {}


@app.post("/triage/text")
async def triage_with_text(request: TextTriageRequest):
    user_input = request.user_input
    initial_state = {
        "emr_fields": {},
        "chat_history": [],
        "last_question": None,
        "last_user_input": user_input,
        "is_complete": False,
        "next_bot_reply": None
    }
    state = triage_graph.invoke(initial_state)

    return {
        "text_reply": state["next_bot_reply"],
        "emr_snapshot": state["emr_fields"]
    }


@app.post("/triage/text/tts")
async def triage_with_text_and_tts(request: TextTriageRequest):
    """Triage endpoint that also returns TTS audio"""
    user_input = request.user_input
    initial_state = {
        "emr_fields": {},
        "chat_history": [],
        "last_question": None,
        "last_user_input": user_input,
        "is_complete": False,
        "next_bot_reply": None
    }
    state = triage_graph.invoke(initial_state)
    
    response = {
        "text_reply": state["next_bot_reply"],
        "emr_snapshot": state["emr_fields"]
    }
    
    # Generate TTS for the response - this is non-blocking for the main response
    try:
        print(f"DEBUG: Attempting TTS for triage response: '{state['next_bot_reply'][:50]}...'")
        audio_url = tts_client.text_to_speech(state["next_bot_reply"])
        
        if audio_url:
            response["audio_url"] = audio_url
            print(f"DEBUG: TTS successful, audio_url added: {audio_url}")
        else:
            print("DEBUG: TTS failed, continuing without audio_url")
            # Response continues without audio_url - frontend fallback will handle this
            
    except Exception as e:
        print(f"ERROR: TTS generation failed with exception: {e}")
        # Response continues without audio_url - this ensures the main request never fails
    
    return response

# Compatibility endpoint for existing frontend
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Frontend compatibility endpoint with session management"""
    message = request.message
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get or create session state
    if session_id not in sessions:
        sessions[session_id] = {
            "emr_fields": {},
            "chat_history": [],
            "last_question": None,
            "is_complete": False
        }
    
    session_state = sessions[session_id]
    
    # Use the triage graph with existing session state
    initial_state = {
        "emr_fields": session_state["emr_fields"],
        "chat_history": session_state["chat_history"],
        "last_question": session_state["last_question"],
        "last_user_input": message,
        "is_complete": session_state["is_complete"],
        "next_bot_reply": None
    }
    
    state = triage_graph.invoke(initial_state)
    
    # Update session state
    sessions[session_id] = {
        "emr_fields": state["emr_fields"],
        "chat_history": state.get("chat_history", []),
        "last_question": state["next_bot_reply"],
        "is_complete": state["is_complete"]
    }
    
    # Determine status based on EMR fields and emergency flag
    status = "active"
    if state["emr_fields"].get("emergency_flag"):
        status = "emergency_detected"
    elif state["is_complete"]:
        status = "complete"
    
    # Map EMR fields to frontend expected format
    emr_data = {
        "patient_info": {
            "chief_complaint": state["emr_fields"].get("chief_complaint", "")
        },
        "symptoms": [state["emr_fields"].get("associated_symptoms", "")],
        "assessment": {
            "severity": state["emr_fields"].get("severity", ""),
            "recommendations": [],
            "next_steps": []
        },
        "triage_level": 1 if state["emr_fields"].get("emergency_flag") else 3
    }
    
    return {
        "ai_message": state["next_bot_reply"],
        "status": status,
        "protocol": "AI Triage Assessment",
        "emr_data": emr_data,
        "messages": [] 
    }



@app.get("/triage/summary")
def get_final_summary(
    chief_complaint: str = Query(...),
    duration: str = Query(...),
    severity: str = Query(...),
    onset: str = Query(...),
    location: str = Query(...),
    associated_symptoms: str = Query(...),
    emergency_flag: bool = Query(False)
):
    # Build EMR dict from query params
    emr = {
        "chief_complaint": chief_complaint,
        "duration": duration,
        "severity": severity,
        "onset": onset,
        "location": location,
        "associated_symptoms": associated_symptoms,
        "emergency_flag": emergency_flag
    }

    # Generate summary using Gemini
    summary_input = summary_prompt(emr)
    summary_response = llm.models.generate_content(model=MODEL_NAME,contents=summary_input)
    summary_text = summary_response.text

    return {
        "summary_text": summary_text,
        "emr_fields": emr
    }


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using the TTS microservice"""
    try:
        print(f"DEBUG: Attempting TTS for standalone request: '{request.text[:50]}...'")
        audio_url = tts_client.text_to_speech(request.text, request.voice)
        
        if audio_url:
            print(f"DEBUG: Standalone TTS successful: {audio_url}")
            return {"audio_url": audio_url, "status": "success"}
        else:
            print("DEBUG: Standalone TTS failed, no audio URL returned")
            return {"error": "Failed to generate audio", "status": "error"}
            
    except Exception as e:
        print(f"ERROR: Standalone TTS generation failed with exception: {e}")
        return {"error": f"TTS service error: {str(e)}", "status": "error"}


# Removed /audio/{filename} endpoint - now using direct TTS service URLs


@app.post("/chat/tts")
async def chat_with_tts(request: ChatRequest):
    """Chat endpoint that also returns TTS audio"""
    # Get regular chat response
    chat_response = await chat_endpoint(request)
    
    # Generate TTS for the AI response - this is non-blocking for the main response
    try:
        ai_message = chat_response["ai_message"]
        print(f"DEBUG: Attempting TTS for chat message: '{ai_message[:50]}...'")
        audio_url = tts_client.text_to_speech(ai_message)
        
        if audio_url:
            chat_response["audio_url"] = audio_url
            print(f"DEBUG: TTS successful, audio_url added: {audio_url}")
        else:
            print("DEBUG: TTS failed, continuing without audio_url")
            # Response continues without audio_url - frontend fallback will handle this
            
    except Exception as e:
        print(f"ERROR: TTS generation failed with exception: {e}")
        # Response continues without audio_url - this ensures the main request never fails
    
    return chat_response


@app.get("/tts/health")
async def tts_health():
    """Check TTS service health"""
    is_healthy = tts_client.health_check()
    provider_info = tts_client.get_provider_info()
    circuit_breaker_status = tts_client.get_circuit_breaker_status()
    
    return {
        "tts_service_healthy": is_healthy,
        "provider_info": provider_info,
        "circuit_breaker_status": circuit_breaker_status
    }

@app.get("/tts/provider")
async def get_tts_provider():
    """Get current TTS provider information"""
    return tts_client.get_provider_info()

