#!/usr/bin/env python3
"""
Test script for TTS microservice integration
"""

import requests
import json
import os
from tts_client import tts_client

def test_tts_health():
    """Test TTS service health check"""
    print("Testing TTS service health...")
    is_healthy = tts_client.health_check()
    print(f"TTS Service Health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
    return is_healthy

def test_direct_tts():
    """Test direct TTS client"""
    print("\nTesting direct TTS client...")
    test_text = "Hello, this is a test of the TTS microservice integration."
    
    audio_path = tts_client.text_to_speech(test_text)
    if audio_path and os.path.exists(audio_path):
        print(f"✓ TTS generated successfully: {audio_path}")
        return True
    else:
        print("✗ TTS generation failed")
        return False

def test_tts_endpoint():
    """Test the /tts endpoint"""
    print("\nTesting /tts endpoint...")
    
    payload = {
        "text": "This is a test of the TTS endpoint.",
        "voice": "female"
    }
    
    try:
        response = requests.post("http://localhost:8000/tts", json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print(f"✓ TTS endpoint working: {result.get('audio_path')}")
                return True
            else:
                print(f"✗ TTS endpoint failed: {result}")
                return False
        else:
            print(f"✗ TTS endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ TTS endpoint connection error: {e}")
        return False

def test_chat_tts_endpoint():
    """Test the /chat/tts endpoint"""
    print("\nTesting /chat/tts endpoint...")
    
    payload = {
        "message": "I have a headache",
        "session_id": "test_session"
    }
    
    try:
        response = requests.post("http://localhost:8000/chat/tts", json=payload)
        if response.status_code == 200:
            result = response.json()
            if "audio_url" in result:
                print(f"✓ Chat TTS endpoint working: {result.get('audio_url')}")
                return True
            else:
                print(f"✗ Chat TTS endpoint missing audio: {result}")
                return False
        else:
            print(f"✗ Chat TTS endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Chat TTS endpoint connection error: {e}")
        return False

def main():
    print("=== TTS Integration Test ===")
    
    # Test TTS service health
    health_ok = test_tts_health()
    
    if not health_ok:
        print("\n⚠️  TTS microservice is not available. Make sure it's running on port 9003.")
        print("Skipping further tests...")
        return
    
    # Test direct TTS client
    direct_ok = test_direct_tts()
    
    # Test API endpoints (requires the FastAPI server to be running)
    print("\n--- Testing API Endpoints (requires FastAPI server running) ---")
    endpoint_ok = test_tts_endpoint()
    chat_tts_ok = test_chat_tts_endpoint()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"TTS Service Health: {'✓' if health_ok else '✗'}")
    print(f"Direct TTS Client: {'✓' if direct_ok else '✗'}")
    print(f"TTS Endpoint: {'✓' if endpoint_ok else '✗'}")
    print(f"Chat TTS Endpoint: {'✓' if chat_tts_ok else '✗'}")
    
    if all([health_ok, direct_ok, endpoint_ok, chat_tts_ok]):
        print("\n🎉 All tests passed! TTS integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()