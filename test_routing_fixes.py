#!/usr/bin/env python3
"""
Test routing fixes for intelligent-triage application
"""

import requests
import json
import time
import sys

def test_routing_fixes():
    print("=== Routing Fixes Test ===\n")
    
    # Use the correct ports for Docker containers
    base_url = "http://localhost:8010"  # Frontend container port
    backend_url = "http://localhost:9001"  # Backend container port
    test_results = []
    
    # Test 1: Root redirect to /intelligent-triage
    print("1. Testing root redirect...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False, timeout=5)
        if response.status_code == 301 and "/intelligent-triage" in response.headers.get('Location', ''):
            print("✅ Root redirects to /intelligent-triage")
            test_results.append(("Root redirect", True))
        else:
            print(f"❌ Root redirect failed: {response.status_code}")
            test_results.append(("Root redirect", False))
    except Exception as e:
        print(f"❌ Root redirect error: {e}")
        test_results.append(("Root redirect", False))
    
    # Test 2: /intelligent-triage should serve the app directly
    print("\n2. Testing /intelligent-triage direct access...")
    try:
        response = requests.get(f"{base_url}/intelligent-triage", timeout=10)
        if response.status_code == 200:
            print("✅ /intelligent-triage serves the app directly")
            test_results.append(("/intelligent-triage direct access", True))
        else:
            print(f"❌ /intelligent-triage not accessible: {response.status_code}")
            test_results.append(("/intelligent-triage direct access", False))
    except Exception as e:
        print(f"❌ /intelligent-triage direct access error: {e}")
        test_results.append(("/intelligent-triage direct access", False))
    
    # Test 3: /intelligent-triage/backend redirect to /intelligent-triage
    print("\n3. Testing /intelligent-triage/backend redirect...")
    try:
        response = requests.get(f"{base_url}/intelligent-triage/backend", allow_redirects=False, timeout=5)
        if response.status_code == 301 and "/intelligent-triage" in response.headers.get('Location', ''):
            print("✅ /intelligent-triage/backend redirects to /intelligent-triage")
            test_results.append(("/intelligent-triage/backend redirect", True))
        else:
            print(f"❌ /intelligent-triage/backend redirect failed: {response.status_code}")
            test_results.append(("/intelligent-triage/backend redirect", False))
    except Exception as e:
        print(f"❌ /intelligent-triage/backend redirect error: {e}")
        test_results.append(("/intelligent-triage/backend redirect", False))
    
    # Test 4: Frontend accessible at /intelligent-triage/
    print("\n4. Testing frontend at /intelligent-triage/...")
    try:
        response = requests.get(f"{base_url}/intelligent-triage/", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible at /intelligent-triage/")
            test_results.append(("Frontend accessibility", True))
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            test_results.append(("Frontend accessibility", False))
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        test_results.append(("Frontend accessibility", False))
    
    # Test 5: Backend API accessible via proxy
    print("\n5. Testing backend API via proxy...")
    try:
        response = requests.get(f"{base_url}/intelligent-triage/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Backend API accessible via proxy")
            test_results.append(("Backend API proxy", True))
        else:
            print(f"❌ Backend API not accessible: {response.status_code}")
            test_results.append(("Backend API proxy", False))
    except Exception as e:
        print(f"❌ Backend API proxy error: {e}")
        test_results.append(("Backend API proxy", False))
    
    # Test 6: Chat API endpoint
    print("\n6. Testing chat API endpoint...")
    try:
        payload = {"message": "Hello", "session_id": "test-session"}
        response = requests.post(f"{base_url}/intelligent-triage/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "ai_message" in data:
                print("✅ Chat API working")
                test_results.append(("Chat API", True))
            else:
                print(f"❌ Chat API response missing ai_message: {data}")
                test_results.append(("Chat API", False))
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            test_results.append(("Chat API", False))
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        test_results.append(("Chat API", False))
    
    # Test 7: TTS API endpoint
    print("\n7. Testing TTS API endpoint...")
    try:
        payload = {"message": "Hello", "session_id": "test-session"}
        response = requests.post(f"{base_url}/intelligent-triage/chat/tts", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "ai_message" in data and "audio_url" in data:
                print("✅ TTS API working")
                test_results.append(("TTS API", True))
            else:
                print(f"❌ TTS API response missing required fields: {data}")
                test_results.append(("TTS API", False))
        else:
            print(f"❌ TTS API failed: {response.status_code}")
            test_results.append(("TTS API", False))
    except Exception as e:
        print(f"❌ TTS API error: {e}")
        test_results.append(("TTS API", False))
    
    # Test 8: Health check
    print("\n8. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check working")
            test_results.append(("Health check", True))
        else:
            print(f"❌ Health check failed: {response.status_code}")
            test_results.append(("Health check", False))
    except Exception as e:
        print(f"❌ Health check error: {e}")
        test_results.append(("Health check", False))
    
    # Test 9: Direct backend access
    print("\n9. Testing direct backend access...")
    try:
        response = requests.get(f"{backend_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Direct backend access working")
            test_results.append(("Direct backend access", True))
        else:
            print(f"❌ Direct backend access failed: {response.status_code}")
            test_results.append(("Direct backend access", False))
    except Exception as e:
        print(f"❌ Direct backend access error: {e}")
        test_results.append(("Direct backend access", False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All routing fixes are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = test_routing_fixes()
    sys.exit(0 if success else 1) 