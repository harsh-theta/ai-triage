# agent_graph.py

from typing import Dict, Optional, List
from google import genai
import os
import json
from prompts import field_prompt, summary_prompt
from dotenv import load_dotenv

load_dotenv()

# --- Setup Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
        response = llm.models.generate_content(model="gemini-2.5-flash", contents=prompt)
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
        response = llm.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[get_emr_summary] LLM summary failed: {e}")
        return "Summary unavailable."

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

    # End if emergency or enough turns or all fields filled
    if emr_fields.get("emergency_flag") or turn >= 8 or not missing:
        session_state["is_complete"] = True
        summary = get_emr_summary(emr_fields)
        bot_reply = summary if summary else "Thank you, I have all the information I need."
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
- If all required fields are filled, or an emergency is detected, summarize the case and end the conversation.
- Only ask one question at a time.

Here is the conversation so far:
{history_str}

Here are the fields still missing: {missing}

If more information is needed, ask the next best question to fill a missing field. If everything is complete, provide a summary and end the conversation.
Respond with only your next message to the user.
"""
    try:
        response = llm.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        bot_reply = response.text.strip()
    except Exception as e:
        print(f"[triage_conversation] LLM question failed: {e}")
        bot_reply = "Could you please clarify your symptoms?"

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
