import requests
import os
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self, base_url: str = None):
        """
        Initialize TTS client for the microservice
        
        Args:
            base_url: Base URL of the TTS microservice (e.g., "http://localhost:9003")
        """
        self.base_url = base_url or os.getenv("TTS_SERVICE_URL", "http://localhost:9003")
        
    def text_to_speech(self, text: str, voice: str = "female", output_dir: str = "audio") -> Optional[str]:
        """
        Convert text to speech using the TTS microservice
        
        Args:
            text: Text to convert to speech
            voice: Voice type (default: "female")
            output_dir: Directory to save the audio file
            
        Returns:
            Path to the generated audio file or None if failed
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique filename
            filename = f"response_{uuid.uuid4().hex[:16]}_{int(uuid.uuid4().int % 10000000000)}.wav"
            output_path = os.path.join(output_dir, filename)
            
            # Prepare request payload
            payload = {
                "text": text,
                "voice": voice
            }
            
            # Make request to TTS microservice
            response = requests.post(
                f"{self.base_url}/tts",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save audio content to file
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"TTS audio saved to: {output_path}")
                return output_path
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