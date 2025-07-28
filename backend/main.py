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
print("-------------------------------")
print(GEMINI_API_KEY)
print("-------------------------------")
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
    
    # Generate TTS for the response
    audio_url = tts_client.text_to_speech(state["next_bot_reply"])
    
    response = {
        "text_reply": state["next_bot_reply"],
        "emr_snapshot": state["emr_fields"]
    }
    
    # Add audio URL if TTS was successful
    if audio_url:
        response["audio_url"] = audio_url
    
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
    audio_url = tts_client.text_to_speech(request.text, request.voice)
    
    if audio_url:
        return {"audio_url": audio_url, "status": "success"}
    else:
        return {"error": "Failed to generate audio", "status": "error"}


# Removed /audio/{filename} endpoint - now using direct TTS service URLs


@app.post("/chat/tts")
async def chat_with_tts(request: ChatRequest):
    """Chat endpoint that also returns TTS audio"""
    # Get regular chat response
    chat_response = await chat_endpoint(request)
    
    # Generate TTS for the AI response
    ai_message = chat_response["ai_message"]
    print(f"DEBUG: Generating TTS for message: '{ai_message}'")
    audio_url = tts_client.text_to_speech(ai_message)
    print(f"DEBUG: TTS result: {audio_url}")
    
    # Add audio URL directly from TTS service
    if audio_url:
        chat_response["audio_url"] = audio_url
        print(f"DEBUG: Added audio_url: {chat_response['audio_url']}")
    else:
        print("DEBUG: No audio_url returned from TTS")
    
    return chat_response


@app.get("/tts/health")
async def tts_health():
    """Check TTS microservice health"""
    is_healthy = tts_client.health_check()
    return {
        "tts_service_healthy": is_healthy,
        "tts_service_url": tts_client.base_url
    }

