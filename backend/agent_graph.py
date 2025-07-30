# agent_graph.py

from typing import Dict, Optional, List
from google import genai
import os
import json
from prompts import summary_prompt
from dotenv import load_dotenv

load_dotenv()

# --- Setup Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
llm = genai.Client(api_key=GEMINI_API_KEY)

REQUIRED_FIELDS = [
    "chief_complaint",
    "duration",
    "severity",
    "onset",
    "location",
    "associated_symptoms",
    "emergency_flag"
]


# Utility: Check for missing fields
def get_missing_fields(emr_fields: dict) -> list:
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in emr_fields or emr_fields[field] in (None, ""):
            missing.append(field)
    return missing


# Extract EMR fields from chat history using LLM
def extract_emr_fields(chat_history: List[Dict]) -> dict:
    history_str = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    ])

    prompt = f"""
        You are a medical assistant. Extract the following EMR fields from this conversation. If a field is not mentioned, leave it blank or null.

        Fields: {REQUIRED_FIELDS}

        For the 'severity' field, only accept values between 1 and 10. If the user gives a value outside this range, set severity to null and ask the user to provide a value between 1 and 10 in your next question.

        Conversation:
        {history_str}

        Return a valid JSON object with the fields as keys.
    """

    try:
        response = llm.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text.replace('```json', '').replace('```', '').strip()
        elif text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
        emr = json.loads(text)
        return emr
    except Exception as e:
        print(f"[extract_emr_fields] LLM extraction failed: {e}")
        return {}


# Summarize EMR dict
def get_emr_summary(emr_fields: dict) -> str:
    prompt = summary_prompt(emr_fields)
    try:
        response = llm.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[get_emr_summary] LLM summary failed: {e}")
        return "Summary unavailable."


# Check if all required questions have been sufficiently addressed
def all_questions_answered(emr_fields: dict, chat_history: List[Dict]) -> bool:
    """
    Check if all required fields have been addressed through questions,
    even if some fields might be empty due to negative responses.
    """
    missing = get_missing_fields(emr_fields)
    
    # If no fields are missing, all questions are answered
    if not missing:
        return True
    
    # Check if we've asked about each missing field in the conversation
    history_text = " ".join([msg["content"].lower() for msg in chat_history if msg["role"] == "assistant"])
    
    # Map fields to question keywords that indicate we've asked about them
    field_keywords = {
        "chief_complaint": ["complaint", "problem", "concern", "symptoms", "feeling", "wrong"],
        "duration": ["long", "duration", "when", "started", "how long", "since when"],
        "severity": ["severe", "pain", "scale", "rate", "intensity", "bad"],
        "onset": ["start", "began", "onset", "sudden", "gradual", "when did"],
        "location": ["where", "location", "area", "part", "body"],
        "associated_symptoms": ["other", "additional", "else", "more", "associated", "along with"],
        "emergency_flag": ["emergency", "urgent", "serious", "hospital", "911", "ambulance"]
    }
    
    # Check if we've asked about each missing field
    for field in missing:
        if field in field_keywords:
            keywords = field_keywords[field]
            if any(keyword in history_text for keyword in keywords):
                # We've asked about this field, so consider it addressed even if empty
                continue
            else:
                # We haven't asked about this field yet
                return False
    
    return True


# Main triage loop
def triage_conversation(user_input: str, session_state: Dict = None) -> Dict:
    if session_state is None:
        session_state = {
            "chat_history": [],
            "emr_fields": {},
            "turn": 0,
            "is_complete": False
        }
    chat_history = session_state["chat_history"]
    emr_fields = session_state["emr_fields"]
    turn = session_state.get("turn", 0)
    is_complete = session_state.get("is_complete", False)

    # Add user message
    chat_history.append({"role": "user", "content": user_input})

    # Extract EMR fields so far
    emr_fields = extract_emr_fields(chat_history)
    missing = get_missing_fields(emr_fields)

    # Check if all questions have been answered (even if some fields are empty)
    questions_complete = all_questions_answered(emr_fields, chat_history)
    
    # End if emergency detected, too many turns, or all questions answered
    if emr_fields.get("emergency_flag") or turn >= 8 or questions_complete:
        session_state["is_complete"] = True
        summary = get_emr_summary(emr_fields)
        bot_reply = summary if summary else "Thank you, I have gathered all the necessary information for your triage assessment."
        chat_history.append({"role": "assistant", "content": bot_reply})
        return {
            "emr_fields": emr_fields,
            "next_bot_reply": bot_reply,
            "is_complete": True,
            "chat_history": chat_history,
            "last_question": bot_reply
        }

    # Let the LLM generate the next question
    history_str = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    ])

    prompt = f"""
        You are a helpful, friendly AI medical triage assistant. Your job is to ask the patient natural, conversational questions to gather the following required fields:
        {REQUIRED_FIELDS}

        - You are directly talking with the user.
        - Do not repeat questions that have already been answered or asked.
        - If the user gives a negative answer (e.g., 'no', 'none', 'nothing else'), accept it and move on to the next field.
        - Only ask one question at a time.
        - Focus on gathering information systematically.

        Here is the conversation so far:
        {history_str}

        Here are the fields still missing: {missing}

        Ask the next best question to fill a missing field. Be conversational and empathetic.
        Respond with only your next message to the user.
    """

    try:
        response = llm.models.generate_content(model=MODEL_NAME, contents=prompt)
        bot_reply = response.text.strip()
    except Exception as e:
        print(f"[triage_conversation] LLM question failed: {e}")
        bot_reply = "Could you please tell me more about your symptoms?"

    chat_history.append({"role": "assistant", "content": bot_reply})
    session_state["turn"] = turn + 1
    session_state["chat_history"] = chat_history
    session_state["emr_fields"] = emr_fields
    session_state["is_complete"] = False
    session_state["last_question"] = bot_reply
    return {
        "emr_fields": emr_fields,
        "next_bot_reply": bot_reply,
        "is_complete": False,
        "chat_history": chat_history,
        "last_question": bot_reply
    }


# For compatibility with main.py

def build_triad_agent():
    class TriageAgent:
        def invoke(self, initial_state: dict) -> dict:
            user_input = initial_state.get("last_user_input", "")
            session_state = {
                "chat_history": initial_state.get("chat_history", []),
                "emr_fields": initial_state.get("emr_fields", {}),
                "turn": initial_state.get("turn", 0),
                "is_complete": initial_state.get("is_complete", False),
                "last_question": initial_state.get("last_question")
            }
            return triage_conversation(user_input, session_state)
    return TriageAgent()
