#!/usr/bin/env python3
"""
Integration test for TTS providers with the main application
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts_client import tts_client

def test_current_provider():
    """Test the current TTS provider"""
    print("=== Current TTS Provider Test ===")
    
    provider_info = tts_client.get_provider_info()
    print(f"Current provider: {provider_info['provider']}")
    print(f"Provider info: {provider_info}")
    
    # Test health check
    health = tts_client.health_check()
    print(f"Health check: {'✅ Healthy' if health else '❌ Unhealthy'}")
    
    # Test TTS generation
    test_text = "This is a test of the current TTS provider configuration."
    print(f"Testing with text: '{test_text}'")
    
    audio_url = tts_client.text_to_speech(test_text)
    
    if audio_url:
        print(f"✅ TTS Success: {audio_url}")
        return True
    else:
        print("❌ TTS Failed")
        return False

def test_provider_switching():
    """Test switching between providers"""
    print("\n=== Provider Switching Test ===")
    
    original_provider = os.environ.get("TTS_PROVIDER", "microservice")
    
    # Test microservice
    print("\n--- Testing Microservice ---")
    os.environ["TTS_PROVIDER"] = "microservice"
    # Reinitialize client to pick up new env var
    from tts_client import TTSClient
    client = TTSClient()
    result1 = client.text_to_speech("Testing microservice provider")
    print(f"Microservice result: {'✅' if result1 else '❌'} {result1}")
    
    # Test Murf
    print("\n--- Testing Murf ---")
    os.environ["TTS_PROVIDER"] = "murf"
    client = TTSClient()
    result2 = client.text_to_speech("Testing Murf provider")
    print(f"Murf result: {'✅' if result2 else '❌'} {result2}")
    
    # Restore original
    os.environ["TTS_PROVIDER"] = original_provider
    
    return bool(result1 and result2)

def main():
    print("TTS Integration Test")
    print("=" * 50)
    
    # Test current provider
    current_test = test_current_provider()
    
    # Test provider switching
    switching_test = test_provider_switching()
    
    print("\n=== Test Summary ===")
    print(f"Current provider test: {'✅ PASS' if current_test else '❌ FAIL'}")
    print(f"Provider switching test: {'✅ PASS' if switching_test else '❌ FAIL'}")
    
    if current_test and switching_test:
        print("🎉 All tests passed! TTS integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()