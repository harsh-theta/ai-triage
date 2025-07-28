import requests
import os
from typing import Optional
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, base_url: str = None):
        """
        Initialize TTS client for the microservice
        
        Args:
            base_url: Base URL of the TTS microservice (e.g., "http://localhost:9003")
        """
        self.base_url = base_url or os.getenv("TTS_SERVICE_URL")
        
    def text_to_speech(self, text: str, voice: str = "female") -> Optional[str]:
        """
        Convert text to speech using the TTS microservice
        
        Args:
            text: Text to convert to speech
            voice: Voice type (default: "female")
            
        Returns:
            Direct audio URL from TTS service or None if failed
        """
        try:
            # Prepare request payload
            payload = {
                "text": text,
                "voice": voice
            }
            
            # Make request to TTS microservice
            response = requests.post(
                f"{self.base_url}/speak",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse JSON response to get audio URL
                response_data = response.json()
                audio_url = response_data.get("audio_url")
                
                if audio_url:
                    logger.info(f"TTS audio URL received: {audio_url}")
                    return audio_url
                else:
                    logger.error(f"No audio_url in TTS response: {response_data}")
                    return None
            else:
                logger.error(f"TTS service error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS service connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"TTS client error: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if the TTS microservice is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# Global TTS client instance
tts_client = TTSClient()