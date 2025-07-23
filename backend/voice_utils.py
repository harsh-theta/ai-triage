# voice_utils.py

import os
import time
import requests
from elevenlabs import generate, save, set_api_key

# --- AssemblyAI Config ---
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"

# --- ElevenLabs Config ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")  # default voice

if ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)

# ---------- STT: AssemblyAI ----------

def upload_audio_to_assemblyai(file_path: str) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    with open(file_path, "rb") as f:
        response = requests.post(ASSEMBLYAI_UPLOAD_URL, headers=headers, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]

def transcribe_audio(file_path: str) -> str:
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("AssemblyAI API key not configured")
    
    upload_url = upload_audio_to_assemblyai(file_path)

    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    json_data = {
        "audio_url": upload_url
    }

    response = requests.post(ASSEMBLYAI_TRANSCRIBE_URL, headers=headers, json=json_data)
    response.raise_for_status()
    transcript_id = response.json()["id"]

    # Poll until done
    status_url = f"{ASSEMBLYAI_TRANSCRIBE_URL}/{transcript_id}"
    while True:
        polling = requests.get(status_url, headers=headers)
        polling.raise_for_status()
        status = polling.json()
        if status["status"] == "completed":
            return status["text"]
        elif status["status"] == "error":
            raise RuntimeError(f"Transcription failed: {status['error']}")
        time.sleep(1.5)

# ---------- TTS: ElevenLabs ----------

def synthesize_speech(text: str, output_path: str) -> str:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ElevenLabs API key not configured")
    
    audio = generate(
        text=text,
        voice=ELEVENLABS_VOICE_ID,
        model="eleven_monolingual_v1"
    )
    save(audio, output_path)
    return output_path
