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

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

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


