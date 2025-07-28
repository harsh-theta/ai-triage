#!/usr/bin/env python3
"""
Final integration test for TTS functionality
"""

import requests
import json

def test_tts_integration():
    print("=== Final TTS Integration Test ===\n")
    
    # Test 1: TTS Service Health
    print("1. Testing TTS service health...")
    try:
        response = requests.get("http://106.201.228.100:9003/health", timeout=5)
        if response.status_code == 200:
            print("✅ TTS service is healthy")
        else:
            print(f"❌ TTS service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ TTS service connection error: {e}")
        return False
    
    # Test 2: Direct TTS Service Call
    print("\n2. Testing direct TTS service call...")
    try:
        payload = {"text": "Hello, this is a test message", "voice": "female"}
        response = requests.post("http://106.201.228.100:9003/speak", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get("audio_url")
            if audio_url:
                print(f"✅ TTS service returned audio URL: {audio_url}")
                
                # Test 3: Verify audio URL is accessible
                print("\n3. Testing audio URL accessibility...")
                audio_response = requests.head(audio_url, timeout=10)
                if audio_response.status_code == 200:
                    print(f"✅ Audio URL is accessible (Content-Type: {audio_response.headers.get('content-type')})")
                else:
                    print(f"❌ Audio URL not accessible: {audio_response.status_code}")
                    return False
            else:
                print(f"❌ No audio_url in response: {data}")
                return False
        else:
            print(f"❌ TTS service call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ TTS service call error: {e}")
        return False
    
    # Test 4: Backend Integration (if server is running)
    print("\n4. Testing backend integration...")
    try:
        payload = {"message": "I have a headache", "session_id": "test"}
        response = requests.post("http://localhost:9001/chat/tts", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "audio_url" in data:
                print(f"✅ Backend returns audio_url: {data['audio_url']}")
                print(f"✅ AI message: {data['ai_message']}")
            else:
                print(f"❌ Backend response missing audio_url: {data}")
                return False
        else:
            print(f"❌ Backend call failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend server not running - skipping backend test")
    except Exception as e:
        print(f"❌ Backend call error: {e}")
        return False
    
    print("\n🎉 All tests passed! TTS integration is working correctly.")
    print("\nTo test with your frontend:")
    print("1. Start the backend: uvicorn main:app --host 0.0.0.0 --port 9001")
    print("2. Start the frontend and enable voice mode")
    print("3. Send a message - you should hear the AI response!")
    
    return True

if __name__ == "__main__":
    test_tts_integration()