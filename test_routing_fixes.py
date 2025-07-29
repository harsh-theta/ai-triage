#!/usr/bin/env python3
"""
Test script to verify the routing fixes for the intelligent-triage deployment
"""

import requests
import time

def test_routing_fixes():
    print("=== Testing Routing Fixes ===\n")
    
    # Test 1: TTS Service Health
    print("1. Testing TTS service...")
    try:
        response = requests.get("http://106.201.228.100:9003/health", timeout=5)
        if response.status_code == 200:
            print("✅ TTS service is healthy")
        else:
            print(f"❌ TTS service issue: {response.status_code}")
    except Exception as e:
        print(f"❌ TTS service error: {e}")
    
    # Test 2: Backend Direct Access
    print("\n2. Testing backend container...")
    try:
        response = requests.get("http://localhost:9001/intelligent-triage/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Backend accessible with proxy path")
        else:
            print(f"❌ Backend proxy path issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
    
    # Test 3: Frontend Container
    print("\n3. Testing frontend container...")
    try:
        response = requests.get("http://localhost:8010/intelligent-triage", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible at /intelligent-triage")
            # Check if it contains expected content
            if "AI Medical Triage System" in response.text:
                print("✅ Frontend content loading correctly")
            else:
                print("⚠️  Frontend content may have issues")
        else:
            print(f"❌ Frontend access issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
    
    # Test 4: API Endpoint through Frontend Proxy
    print("\n4. Testing API through frontend proxy...")
    try:
        payload = {"message": "I have a headache", "session_id": "test"}
        response = requests.post(
            "http://localhost:8010/intelligent-triage/chat/tts", 
            json=payload, 
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if "audio_url" in data:
                print("✅ API proxy working - TTS integration successful!")
                print(f"✅ Audio URL: {data['audio_url']}")
            else:
                print("⚠️  API working but no audio_url (check TTS integration)")
        else:
            print(f"❌ API proxy issue: {response.status_code}")
    except Exception as e:
        print(f"❌ API proxy error: {e}")
    
    print("\n" + "="*50)
    print("🚀 DEPLOYMENT INSTRUCTIONS:")
    print("="*50)
    print("1. Deploy: ./deploy.sh")
    print("2. Check status: docker-compose ps")
    print("3. View logs: docker-compose logs -f")
    print("4. Access app: https://demo.thehealthmolasses.com/intelligent-triage")
    print("\n📱 Expected URLs:")
    print("   Frontend: https://demo.thehealthmolasses.com/intelligent-triage")
    print("   API Docs: https://demo.thehealthmolasses.com/intelligent-triage/docs")
    print("   Health: https://demo.thehealthmolasses.com/intelligent-triage/tts/health")

if __name__ == "__main__":
    test_routing_fixes()