# triage_agent.py

from typing import Dict, List, Optional
from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- Setup Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
llm = genai.Client(api_key=GEMINI_API_KEY)

# System prompt for the medical triage interviewer
TRIAGE_SYSTEM_PROMPT = """
You are a medical triage interviewer conducting a patient interview. Your objective is to gather comprehensive information about the patient's symptoms and health condition.

Key instructions:
- Ask one clear, concise question at a time (maximum 20 words)
- Be empathetic, professional, and conversational
- Do not repeat questions you have already asked
- Focus on gathering detailed information about:
  * Chief complaint and main concern
  * Duration and timing of symptoms
  * Severity and intensity
  * Location and radiation of symptoms
  * Associated symptoms
  * Triggers and relieving factors
  * Impact on daily activities
- Ask follow-up questions to clarify vague answers
- Be natural and human-like, not robotic or clinical
- Show genuine concern and empathy
- Stop after 12 questions maximum
"""

# Emergency detection patterns - COMMENTED OUT
# EMERGENCY_PATTERNS = [
#     "chest pain", "chest pressure", "heart attack", "cardiac",
#     "shortness of breath", "difficulty breathing", "can't breathe", "choking",
#     "loss of consciousness", "unconscious", "seizure", "stroke",
#     "uncontrolled bleeding", "severe bleeding", "major trauma",
#     "vomiting blood", "appendicitis", "anaphylaxis", "throat closing",
#     "overdose", "poisoning", "suicide", "self harm",
#     "emergency", "911", "ambulance", "hospital"
# ]

# def detect_emergency(text: str) -> bool:
#     """Check if the text contains emergency symptoms"""
#     text_lower = text.lower()
#     return any(pattern in text_lower for pattern in EMERGENCY_PATTERNS)

def _sanitize_json_text(text: str) -> str:
    """Attempt to coerce LLM output into valid JSON text by removing fences and fixing common issues."""
    # Strip code fences
    t = text.strip()
    if t.startswith('```'):
        lines = t.split('\n')
        if len(lines) >= 2:
            # remove first and last fence-like lines
            if lines[-1].strip().startswith('```'):
                t = '\n'.join(lines[1:-1]).strip()
            else:
                t = '\n'.join(lines[1:]).strip()
    # Replace smart quotes
    t = t.replace('\u201c', '"').replace('\u201d', '"').replace('“', '"').replace('”', '"').replace("’", "'")
    # If multiple JSONs, take first balanced braces
    if not t.strip().startswith('{'):
        # try to find first '{' and last '}'
        start = t.find('{')
        end = t.rfind('}')
        if start != -1 and end != -1 and end > start:
            t = t[start:end+1]
    # Remove trailing commas before closing braces/brackets (common LLM error)
    t = t.replace(',\n}', '\n}').replace(',\n ]', '\n ]').replace(',\n]', '\n]')
    return t


def _strip_markdown(text: str) -> str:
    """Remove common markdown/formatting characters for plain text rendering."""
    if not text:
        return text
    t = text
    # Remove code fences
    if t.strip().startswith('```'):
        lines = t.split('\n')
        if len(lines) >= 2:
            if lines[-1].strip().startswith('```'):
                t = '\n'.join(lines[1:-1])
            else:
                t = '\n'.join(lines[1:])
    # Strip leading markdown bullets and hashes per line
    cleaned_lines = []
    for line in t.split('\n'):
        s = line.lstrip()
        # remove common bullet markers
        for prefix in ['- ', '* ', '• ', '+ ', '> ', '# ', '## ', '### ', '-\t', '*\t']:
            if s.startswith(prefix):
                s = s[len(prefix):]
                break
        cleaned_lines.append(s)
    t = '\n'.join(cleaned_lines)
    # Remove stray asterisks/backticks/underscores used for emphasis
    for ch in ['*', '`', '_']:
        t = t.replace(ch, '')
    # Collapse excessive blank lines
    t = '\n'.join([ln for ln in t.split('\n') if ln.strip() != '' or True])
    return t.strip()


def _single_turn_llm(conversation_history: List[Dict], turn_number: int) -> Dict:
    """Perform a single LLM call that returns next question, updated summary, end flag, and extracted fields."""
    conversation_str = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history
    ])

    prompt = f"""
    {TRIAGE_SYSTEM_PROMPT}

    Conversation so far:\n{conversation_str}

    Task:
    - Produce ONE next question to ask the patient (<= 20 words)
    - Update a concise, clinically useful report (summary) based on everything so far
    - IMPORTANT: The summary MUST be plain text without any Markdown or formatting characters
      (avoid *, -, •, #, >, `, headings, bold/italic). Use simple sentences or short lines.
    - Decide if you have enough information to end the interview now
    - Optionally extract basic fields if clearly stated

    Return ONLY valid JSON with this exact schema:
    {{
      "next_question": string,              // your single next question; if should_end=true, put an empty string
      "updated_summary": string,            // full Markdown report to show to clinician
      "should_end": boolean,                // true if enough information has been gathered
      "extracted_fields": {{                // optional lightweight fields for UI; omit if unsure
        "chief_complaint": string|null,
        "duration": string|null,
        "severity": string|number|null,
        "onset": string|null,
        "location": string|null,
        "associated_symptoms": string|array|null
      }}
    }}
    """

    try:
        response = llm.models.generate_content(model=MODEL_NAME, contents=prompt)
        raw_text = response.text.strip()
        text = _sanitize_json_text(raw_text)
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("LLM did not return a JSON object")
        # Normalize fields
        data.setdefault("next_question", "")
        data.setdefault("updated_summary", "")
        data.setdefault("should_end", False)
        data.setdefault("extracted_fields", {})
        return data
    except Exception as e:
        print(f"[_single_turn_llm] Error: {e}")
        # Fallback minimal response
        return {
            "next_question": "Could you please tell me more about your symptoms?",
            "updated_summary": "Summary unavailable.",
            "should_end": False,
            "extracted_fields": {}
        }

def generate_medical_summary(conversation_history: List[Dict]) -> str:
    """Deprecated in favor of single-call loop; kept as fallback."""
    try:
        data = _single_turn_llm(conversation_history, len(conversation_history))
        return data.get("updated_summary", "Summary unavailable.")
    except Exception:
        return "Summary unavailable."

def triage_conversation(user_input: str, session_state: Dict = None) -> Dict:
    """
    Main triage conversation function
    Returns the same format as the original agent_graph for compatibility
    """
    if session_state is None:
        session_state = {
            "chat_history": [],
            "emr_fields": {},
            "turn": 0,
            "is_complete": False,
            "last_question": None
        }
    
    chat_history = session_state["chat_history"]
    turn = session_state.get("turn", 0)
    is_complete = session_state.get("is_complete", False)
    
    # Check for early exit commands
    if user_input.lower() in ["quit", "exit", "stop", "end", "done", "finish"]:
        session_state["is_complete"] = True
        
        # Generate final comprehensive summary
        final_summary = generate_medical_summary(chat_history)
        session_state["emr_fields"]["medical_summary"] = final_summary
        
        bot_reply = "Thank you for your time. The triage session has ended."
        chat_history.append({"role": "assistant", "content": bot_reply})
        return {
            "emr_fields": session_state["emr_fields"],
            "next_bot_reply": bot_reply,
            "is_complete": True,
            "chat_history": chat_history,
            "last_question": bot_reply,
            "medical_summary": final_summary,
            "updated_report": final_summary
        }
    
    # Add user message to history
    chat_history.append({"role": "user", "content": user_input})

    # If we've hit hard limit, end with a final summary using single-turn LLM
    if turn >= 12 or is_complete:
        data = _single_turn_llm(chat_history, turn + 1)
        final_summary = data.get("updated_summary", "Summary unavailable.")
        session_state["emr_fields"].update(data.get("extracted_fields", {}))
        session_state["emr_fields"]["medical_summary"] = final_summary

        bot_reply = "Thank you, I have gathered all the necessary information for your triage assessment."
        chat_history.append({"role": "assistant", "content": bot_reply})
        return {
            "emr_fields": session_state["emr_fields"],
            "next_bot_reply": bot_reply,
            "is_complete": True,
            "chat_history": chat_history,
            "last_question": bot_reply,
            "medical_summary": final_summary,
            "updated_report": final_summary
        }

    # Single LLM call for this turn
    previous_summary = session_state["emr_fields"].get("medical_summary")
    data = _single_turn_llm(chat_history, turn + 1)
    next_question = data.get("next_question", "Could you please tell me more about your symptoms?")
    updated_summary_raw = data.get("updated_summary") or previous_summary or "Summary unavailable."
    updated_summary = _strip_markdown(updated_summary_raw)
    should_end = bool(data.get("should_end", False))
    extracted = data.get("extracted_fields", {}) or {}

    # Add bot response
    bot_reply = next_question if not should_end else "Thank you, I have gathered all the necessary information for your triage assessment."
    chat_history.append({"role": "assistant", "content": bot_reply})

    # Update state
    session_state["turn"] = turn + 1
    session_state["chat_history"] = chat_history
    session_state["is_complete"] = should_end
    session_state["last_question"] = bot_reply
    session_state["emr_fields"].update(extracted)
    session_state["emr_fields"]["medical_summary"] = updated_summary

    return {
        "emr_fields": session_state["emr_fields"],
        "next_bot_reply": bot_reply,
        "is_complete": should_end,
        "chat_history": chat_history,
        "last_question": bot_reply,
        "medical_summary": updated_summary,
        "updated_report": updated_summary
    }

def build_triad_agent():
    """
    Build the triage agent for compatibility with main.py
    This maintains the same interface as the original agent_graph
    """
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

# For direct testing/usage
if __name__ == "__main__":
    # Example usage
    agent = build_triad_agent()
    
    # Simulate a conversation
    state = {
        "chat_history": [],
        "emr_fields": {},
        "turn": 0,
        "is_complete": False,
        "last_question": None,
        "last_user_input": "I have a headache"
    }
    
    result = agent.invoke(state)
    print("Bot:", result["next_bot_reply"])
    if "medical_summary" in result:
        print("Summary:", result["medical_summary"])
