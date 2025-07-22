import os
import json
import logging
from typing import Any, Dict, List, Optional, TypedDict
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph

# =========================
# Config & Environment
# =========================

load_dotenv()
logging.basicConfig(level=logging.INFO)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY is not set in the environment.")
    raise RuntimeError("GOOGLE_API_KEY is required for Gemini API access.")

genai.configure(api_key=GOOGLE_API_KEY)

# =========================
# Models
# =========================

class UserInput(BaseModel):
    message: str
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    ai_message: str
    emr_data: Dict[str, Any]
    status: str
    protocol: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None

class TriageState(TypedDict):
    messages: list
    patient_data: dict
    status: str
    conversation_summary: str

# =========================
# Session Management
# =========================

session_states: Dict[str, TriageState] = {}

def get_or_create_session(session_id: str) -> TriageState:
    """Initialize or retrieve a session state."""
    if session_id not in session_states:
        # Add initial greeting message
        initial_message = {
            "role": "assistant",
            "content": "Hello! I'm your AI triage assistant. I'm here to help gather information about your medical concerns for healthcare professionals. Please describe what's bothering you today or what symptoms you're experiencing."
        }
        session_states[session_id] = TriageState(
            messages=[initial_message],
            patient_data={},
            status="active",
            conversation_summary=""
        )
    return session_states[session_id]

# =========================
# LLM Helper Functions
# =========================

def get_triage_system_prompt() -> str:
    """System prompt for the triage assistant."""
    return """You are a professional medical triage assistant. Your role is to:

1. Gather information about the patient's symptoms and medical concerns through natural conversation
2. Ask relevant follow-up questions to understand the severity and nature of their condition
3. Collect important medical information (symptoms, duration, severity, medical history, etc.)
4. NEVER diagnose conditions or recommend specific treatments/medications
5. NEVER provide medical advice - only gather information for healthcare professionals

EMERGENCY DETECTION:
If you detect any of these emergency symptoms, immediately respond with "EMERGENCY_DETECTED" at the start of your message:
- Chest pain with difficulty breathing
- Severe difficulty breathing or shortness of breath
- Signs of stroke (sudden weakness, speech problems, facial drooping)
- Severe allergic reactions
- Unconsciousness or altered mental state
- Severe bleeding or trauma
- Severe abdominal pain
- Signs of heart attack
- Poisoning or overdose
- Severe burns

CONVERSATION STYLE:
- Be empathetic and professional
- Ask one or two questions at a time
- Use simple, clear language
- Show concern for their wellbeing
- Gather comprehensive information systematically

Remember: You are gathering information for healthcare professionals, not providing medical advice."""

def call_gemini_for_triage(conversation_history: List[Dict], user_message: str) -> Dict[str, Any]:
    """Call Gemini API for triage conversation."""
    try:
        # Build conversation context
        context = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Patient" if msg["role"] == "user" else "Triage Assistant"
            context += f"{role}: {msg['content']}\n"
        
        prompt = f"""{get_triage_system_prompt()}

CONVERSATION HISTORY:
{context}

CURRENT PATIENT MESSAGE: {user_message}

Please respond as the triage assistant. If this is an emergency, start your response with "EMERGENCY_DETECTED".

Also provide a JSON summary of information gathered so far with these fields:
- chief_complaint: Main concern in a few words
- symptoms: List of symptoms mentioned
- duration: How long symptoms have been present
- severity: Patient's description of severity (mild/moderate/severe)
- additional_info: Any other relevant medical information
- questions_asked: Number of questions you've asked so far

Format your response as:
RESPONSE: [Your conversational response here]
JSON_DATA: [JSON object with the summary]"""

        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text
        
        # Check for emergency
        is_emergency = response_text.startswith("EMERGENCY_DETECTED")
        if is_emergency:
            response_text = response_text.replace("EMERGENCY_DETECTED", "").strip()
        
        # Extract response and JSON data
        parts = response_text.split("JSON_DATA:")
        ai_response = parts[0].replace("RESPONSE:", "").strip()
        
        # Extract JSON data if present
        emr_data = {}
        if len(parts) > 1:
            try:
                json_part = parts[1].strip()
                # Clean up the JSON part
                if json_part.startswith("```json"):
                    json_part = json_part.replace("```json", "").replace("```", "").strip()
                emr_data = json.loads(json_part)
            except:
                logging.warning("Could not parse JSON data from response")
        
        return {
            "ai_message": ai_response,
            "is_emergency": is_emergency,
            "emr_data": emr_data
        }
        
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return {
            "ai_message": "I apologize, but I'm having technical difficulties. Please describe your symptoms again, and if this is an emergency, please call 911 immediately.",
            "is_emergency": False,
            "emr_data": {}
        }

# =========================
# Triage Logic
# =========================

def process_triage_message(state: TriageState, user_message: str) -> TriageState:
    """Process a user message through the LLM-driven triage system."""
    try:
        # Call Gemini for triage conversation
        result = call_gemini_for_triage(state["messages"], user_message)
        
        # Add AI response to messages
        ai_message = {
            "role": "assistant",
            "content": result["ai_message"]
        }
        state["messages"].append(ai_message)
        
        # Update patient data with new information
        if result["emr_data"]:
            state["patient_data"].update(result["emr_data"])
        
        # Update status based on emergency detection
        if result["is_emergency"]:
            state["status"] = "emergency_detected"
        else:
            state["status"] = "active"
            
        return state
        
    except Exception as e:
        logging.error(f"Triage processing error: {e}")
        # Add error message
        error_message = {
            "role": "assistant", 
            "content": "I apologize, but I'm experiencing technical difficulties. Please describe your symptoms again, and if this is an emergency, please call 911 immediately."
        }
        state["messages"].append(error_message)
        state["status"] = "error"
        return state

# =========================
# FastAPI App & Endpoints
# =========================

app = FastAPI(title="AI Triage System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for service info."""
    return {"message": "AI Triage System API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-triage-system"}

@app.post("/chat", response_model=AIResponse)
async def chat_endpoint(user_input: UserInput, request: Request):
    """Main chat endpoint for triage conversation."""
    session_id = user_input.session_id or str(request.client.host)
    try:
        # Get or create session state
        state = get_or_create_session(session_id)

        # Add the user message to conversation history
        user_message = {"role": "user", "content": user_input.message}
        state["messages"].append(user_message)

        # Process the message through LLM-driven triage
        final_state = process_triage_message(state, user_input.message)
        
        # Update session state
        session_states[session_id] = final_state
        
        # Get the latest AI message
        ai_message = final_state["messages"][-1]["content"] if final_state["messages"] else "Hello! I'm here to help assess your medical concerns. Please describe what's bothering you today."
        
        return AIResponse(
            ai_message=ai_message,
            emr_data=final_state["patient_data"],
            status=final_state["status"],
            protocol="AI Triage Assistant",
            messages=final_state["messages"]
        )
        
    except Exception as e:
        logging.error(f"/chat endpoint error: {e}")
        return AIResponse(
            ai_message="I apologize, but I'm experiencing technical difficulties. Please describe your symptoms again, and if this is an emergency, please call 911 immediately.",
            emr_data={},
            status="error",
            protocol="AI Triage Assistant",
            messages=[]
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)