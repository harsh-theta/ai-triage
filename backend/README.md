## 🩺 AI-Powered Intelligent Triage – PoC

This is a **plug-and-play Proof of Concept (PoC)** for an AI-powered medical triage assistant. The system:

* Talks to users via voice or text.
* Asks intelligent follow-up questions.
* Gathers all required EMR information.
* Detects emergencies and ends the session appropriately.
* Returns a structured EMR JSON output + final natural language summary.
* Works entirely over API (no database or frontend required).

---

## ✨ Key Features

| Feature                    | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| ✅ Gemini-powered AI        | Uses Google Gemini to power dynamic, human-like triage |
| 🧠 LangGraph state machine | Handles controlled flow: ask → extract → complete      |
| 🎤 Voice input             | AssemblyAI STT converts voice to text                  |
| 🔈 Voice output            | ElevenLabs TTS converts bot replies to audio           |
| 🔄 Stateless               | No database; responses are generated per request       |
| 🧾 EMR-ready output        | JSON format compatible with future EMR integration     |

---

## 🧱 Project Structure

```bash
/triage_ai_poc
├── main.py            # FastAPI app with API endpoints
├── agent_graph.py     # LangGraph state machine (Gemini + EMR logic)
├── voice_utils.py     # STT (AssemblyAI) + TTS (ElevenLabs)
├── prompts.py         # Prompt templates for Gemini
├── models.py          # (Optional) Pydantic models (to be added later)
├── uploads/           # Temporary uploads of user audio
├── responses/         # Synthesized voice reply audio files
└── README.md          # You're here!
```

---

## 🧠 Triage Workflow

1. User speaks or types their complaint.
2. AI triage assistant begins asking questions.
3. Each answer updates the `emr_fields` dictionary.
4. If emergency symptoms are detected → conversation ends.
5. When all fields are collected:

   * AI stops asking questions.
   * Generates summary + JSON output.
6. (Optional) Synthesizes the summary as speech.

---

## ✅ Required EMR Fields Collected

These are the **minimum fields** the AI agent gathers during triage:

* `chief_complaint`
* `duration`
* `severity`
* `onset`
* `location`
* `associated_symptoms`
* `emergency_flag`

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install fastapi uvicorn openai google-generativeai langgraph elevenlabs requests
```

### 2. Set Environment Variables

Create a `.env` file or export the following:

```bash
export GEMINI_API_KEY=your_gemini_key
export ASSEMBLYAI_API_KEY=your_assemblyai_key
export ELEVENLABS_API_KEY=your_elevenlabs_key
export ELEVENLABS_VOICE_ID=Rachel  # or Adam, Bella, etc.
```

### 3. Run FastAPI Server

```bash
uvicorn main:app --reload
```

---

## 📂 What to Do in Each File

### ✅ `main.py`

* Provides the API interface.
* `/triage/voice`: Accepts audio input, returns bot reply (text + audio).
* `/triage/text`: Accepts text input.
* `/triage/summary`: Returns final EMR + summary.
* Add additional routes if needed (e.g., memory-based sessions later).

### ✅ `agent_graph.py`

* Core LangGraph logic: builds triage flow.
* State machine steps:

  * `ask_question`
  * `process_input`
  * `summarize`
* Modifies state and returns the bot’s next response.

### ✅ `voice_utils.py`

* Handles speech input/output.
* `transcribe_audio()`: Uses AssemblyAI STT.
* `synthesize_speech()`: Uses ElevenLabs TTS.
* You can extend this to support multiple voices or formats.

### ✅ `prompts.py`

* Central place for all LLM prompts.
* Contains:

  * System instructions
  * Per-field question templates
  * Extraction and summarization prompts

---

## 📬 API Endpoints

| Method | Endpoint          | Description                         |
| ------ | ----------------- | ----------------------------------- |
| `POST` | `/triage/voice`   | Upload audio, get voice+text reply  |
| `POST` | `/triage/text`    | Send text input, get next bot reply |
| `GET`  | `/triage/summary` | Return final EMR + summary + audio  |

---

## 🔮 Future Enhancements

* Persistent session handling with token/memory
* Frontend UI (Streamlit, React, or mobile)
* Feedback/correction loop
* Chronic patient follow-ups
* Integration with EMR systems (FHIR, HL7)

---

## 🧪 Example Text Test

```bash
curl -X POST http://localhost:8000/triage/text \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I’ve had a fever and chills since yesterday."}'
```
