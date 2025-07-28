#!/usr/bin/env python3
"""
Test Docker routing for TTS integration
"""

import requests
import json
import time

def test_docker_routing():
    print("=== Docker Routing Test for TTS Integration ===\n")
    
    # Test 1: TTS Service Health (external)
    print("1. Testing external TTS service...")
    try:
        response = requests.get("http://106.201.228.100:9003/health", timeout=5)
        if response.status_code == 200:
            print("✅ External TTS service is healthy")
        else:
            print(f"❌ TTS service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ TTS service connection error: {e}")
        return False
    
    # Test 2: Backend container (direct access)
    print("\n2. Testing backend container direct access...")
    try:
        response = requests.get("http://localhost:9001/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Backend container accessible on localhost:9001")
        else:
            print(f"❌ Backend container not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend container connection error: {e}")
        print("   Make sure containers are running: docker-compose up -d")
        return False
    
    # Test 3: Backend API endpoint (without proxy prefix)
    print("\n3. Testing backend API endpoint (internal routing)...")
    try:
        payload = {"message": "I have a headache", "session_id": "test"}
        response = requests.post("http://localhost:9001/chat/tts", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "audio_url" in data:
                print(f"✅ Backend API working - audio_url: {data['audio_url']}")
                print(f"✅ AI message: {data['ai_message'][:50]}...")
                
                # Test 4: Verify audio URL accessibility
                print("\n4. Testing audio URL accessibility...")
                audio_response = requests.head(data['audio_url'], timeout=10)
                if audio_response.status_code == 200:
                    print(f"✅ Audio URL accessible (Content-Type: {audio_response.headers.get('content-type')})")
                else:
                    print(f"❌ Audio URL not accessible: {audio_response.status_code}")
                    return False
            else:
                print(f"❌ Backend response missing audio_url: {data}")
                return False
        else:
            print(f"❌ Backend API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend API call error: {e}")
        return False
    
    # Test 5: Frontend container
    print("\n5. Testing frontend container...")
    try:
        response = requests.get("http://localhost:8010", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend container accessible on localhost:8010")
        else:
            print(f"❌ Frontend container not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend container connection error: {e}")
        return False
    
    # Test 6: Proxy routing (if available)
    print("\n6. Testing proxy routing...")
    try:
        # Test backend with proxy prefix
        response = requests.get("http://localhost:9001/intelligent-triage/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend proxy routing working")
        else:
            print("⚠️  Backend proxy routing not working (this is expected for internal Docker communication)")
    except Exception as e:
        print("⚠️  Backend proxy routing not available (this is expected for internal Docker communication)")
    
    print("\n🎉 Docker routing test completed!")
    print("\n📋 Summary:")
    print("✅ External TTS service: Working")
    print("✅ Backend container: Working") 
    print("✅ Backend API (internal): Working")
    print("✅ Audio URLs: Accessible")
    print("✅ Frontend container: Working")
    
    print("\n🚀 Next steps:")
    print("1. Frontend should call backend at: http://backend:9001/chat/tts (internal Docker network)")
    print("2. External users access via: demo.company.com/intelligent-triage/")
    print("3. The proxy handles the /intelligent-triage prefix routing")
    
    return True

if __name__ == "__main__":
    test_docker_routing()