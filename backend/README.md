# AI-Powered Intelligent Triage

A medical triage assistant that gathers patient information and detects emergencies using Google Gemini.

## Project Structure

- `main.py`: FastAPI application and API endpoints.
- `triage_agent.py`: Core logic for the triage conversation and state management.
- `voice_utils.py`: Utilities for Speech-to-Text (AssemblyAI) and Text-to-Speech (ElevenLabs).
- `prompts.py`: System prompts for the LLM.

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn openai google-generativeai elevenlabs requests python-dotenv
   ```

2. Set environment variables in a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_key
   ASSEMBLYAI_API_KEY=your_assemblyai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ELEVENLABS_VOICE_ID=your_voice_id
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/triage/voice` | Upload audio, get voice+text reply |
| POST | `/triage/text` | Send text input, get next bot reply |
| GET | `/triage/summary` | Return final EMR + summary |

## Example Usage

```bash
curl -X POST http://localhost:8000/triage/text \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I have a headache"}'
```
