#!/usr/bin/env python3
"""
Simple test for TTS integration without the full agent graph
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tts_client import tts_client
import uvicorn

app = FastAPI(root_path="/intelligent-triage")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/chat/tts")
async def chat_with_tts(request: ChatRequest):
    """Simple chat endpoint that returns TTS audio"""
    
    # Simple response for testing
    ai_message = f"I understand you said: '{request.message}'. How can I help you further?"
    
    # Generate TTS for the AI response
    print(f"DEBUG: Generating TTS for message: '{ai_message}'")
    audio_url = tts_client.text_to_speech(ai_message)
    print(f"DEBUG: TTS result: {audio_url}")
    
    response = {
        "ai_message": ai_message,
        "status": "active",
        "protocol": "Simple Test",
        "emr_data": {},
        "messages": []
    }
    
    # Add audio URL directly from TTS service
    if audio_url:
        response["audio_url"] = audio_url
        print(f"DEBUG: Added audio_url: {response['audio_url']}")
    else:
        print("DEBUG: No audio_url returned from TTS")
    
    return response

@app.get("/tts/health")
async def tts_health():
    """Check TTS microservice health"""
    is_healthy = tts_client.health_check()
    return {
        "tts_service_healthy": is_healthy,
        "tts_service_url": tts_client.base_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)