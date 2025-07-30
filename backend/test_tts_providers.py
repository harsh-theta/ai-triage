#!/usr/bin/env python3
"""
Test script to verify both TTS providers work correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts_client import TTSClient

def test_microservice_tts():
    """Test microservice TTS"""
    print("\n=== Testing Microservice TTS ===")
    
    # Temporarily set provider to microservice
    original_provider = os.environ.get("TTS_PROVIDER")
    os.environ["TTS_PROVIDER"] = "microservice"
    
    try:
        client = TTSClient()
        print(f"Provider: {client.tts_provider}")
        print(f"Health check: {client.health_check()}")
        
        # Test TTS generation
        test_text = "Hello, this is a test of the microservice TTS."
        audio_url = client.text_to_speech(test_text)
        
        if audio_url:
            print(f"✅ Microservice TTS Success: {audio_url}")
        else:
            print("❌ Microservice TTS Failed")
            
    except Exception as e:
        print(f"❌ Microservice TTS Error: {e}")
    finally:
        # Restore original provider
        if original_provider:
            os.environ["TTS_PROVIDER"] = original_provider
        elif "TTS_PROVIDER" in os.environ:
            del os.environ["TTS_PROVIDER"]

def test_murf_tts():
    """Test Murf TTS"""
    print("\n=== Testing Murf TTS ===")
    
    # Temporarily set provider to murf
    original_provider = os.environ.get("TTS_PROVIDER")
    os.environ["TTS_PROVIDER"] = "murf"
    
    try:
        client = TTSClient()
        print(f"Provider: {client.tts_provider}")
        print(f"Health check: {client.health_check()}")
        print(f"Provider info: {client.get_provider_info()}")
        
        # Test TTS generation
        test_text = "Hello, this is a test of the Murf TTS API."
        audio_url = client.text_to_speech(test_text)
        
        if audio_url:
            print(f"✅ Murf TTS Success: {audio_url}")
        else:
            print("❌ Murf TTS Failed")
            
    except Exception as e:
        print(f"❌ Murf TTS Error: {e}")
    finally:
        # Restore original provider
        if original_provider:
            os.environ["TTS_PROVIDER"] = original_provider
        elif "TTS_PROVIDER" in os.environ:
            del os.environ["TTS_PROVIDER"]

def main():
    print("TTS Providers Test Script")
    print("=" * 40)
    
    # Test both providers
    test_microservice_tts()
    test_murf_tts()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()