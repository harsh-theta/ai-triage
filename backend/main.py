from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from agent_graph import build_triad_agent
# from voice_utils import transcribe_audio, synthesize_speech
import uuid
import os
from fastapi import Query
from prompts import summary_prompt
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAHK_B3M7P-lfPx_z2sF0AtiPUQLkTQP-o")

# --- Setup Gemini ---
llm = genai.Client(api_key=GEMINI_API_KEY)

# Request models
class TextTriageRequest(BaseModel):
    user_input: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

app = FastAPI()

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store audio responses
os.makedirs("responses", exist_ok=True)

# Build the agent once
triage_graph = build_triad_agent()

# In-memory session storage
sessions = {}


# @app.post("/triage/voice")
# async def triage_with_voice(
#     audio: UploadFile = File(...),
#     session_id: str = Form(default_factory=lambda: str(uuid.uuid4())),
#     voice_mode: bool = Form(default=True)
# ):
#     # Save uploaded audio
#     audio_path = f"uploads/{session_id}-{audio.filename}"
#     os.makedirs("uploads", exist_ok=True)
#     with open(audio_path, "wb") as f:
#         f.write(await audio.read())

#     # STT → Get text
#     user_text = transcribe_audio(audio_path)

#     # Run LangGraph agent
#     initial_state = {
#         "emr_fields": {},
#         "chat_history": [],
#         "last_question": None,
#         "last_user_input": user_text,
#         "is_complete": False,
#         "next_bot_reply": None
#     }
#     state = triage_graph.invoke(initial_state)

#     text_reply = state["next_bot_reply"]
#     audio_url = None

#     # TTS → If voice mode, convert response to audio
#     if voice_mode:
#         audio_filename = f"{session_id}-reply.mp3"
#         audio_path = f"responses/{audio_filename}"
#         synthesize_speech(text_reply, audio_path)
#         audio_url = f"/responses/{audio_filename}"

#     return {
#         "text_reply": text_reply,
#         "audio_reply_url": audio_url,
#         "emr_snapshot": state["emr_fields"],
#         "session_id": session_id
#     }


# @app.get("/responses/{filename}")
# async def get_audio_file(filename: str):
#     file_path = os.path.join("responses", filename)
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="audio/mpeg")
#     return JSONResponse(status_code=404, content={"error": "File not found"})


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
        "messages": []  # Could be populated with chat history if needed
    }



@app.get("/triage/summary")
def get_final_summary(
    chief_complaint: str = Query(...),
    duration: str = Query(...),
    severity: str = Query(...),
    onset: str = Query(...),
    location: str = Query(...),
    associated_symptoms: str = Query(...),
    emergency_flag: bool = Query(False),
    # voice_mode: bool = Query(False)
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
    summary_response = llm.models.generate_content(model="gemini-2.5-flash",contents=summary_input)
    summary_text = summary_response.text

    # audio_url = None
    # if voice_mode:
    #     session_id = str(uuid.uuid4())
    #     audio_filename = f"{session_id}-final-summary.mp3"
    #     audio_path = f"responses/{audio_filename}"
    #     synthesize_speech(summary_text, audio_path)
    #     audio_url = f"/responses/{audio_filename}"

    return {
        "summary_text": summary_text,
        "emr_fields": emr,
        # "audio_reply_url": audio_url
    }


