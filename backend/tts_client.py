import requests
import os
from typing import Optional
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Import Murf client
try:
    from murf import Murf
    MURF_AVAILABLE = True
except ImportError:
    MURF_AVAILABLE = False
    logger.warning("Murf library not available. Install with: pip install murf")

class TTSClient:
    def __init__(self, base_url: str = None):
        """
        Initialize TTS client with support for multiple providers
        
        Args:
            base_url: Base URL of the TTS microservice (e.g., "http://localhost:9003")
        """
        # Microservice configuration
        self.base_url = base_url or os.getenv("TTS_SERVICE_URL")
        self.proxy_domain = os.getenv("PROXY_DOMAIN", "https://demo.thetatechnolabs.com")
        self.proxy_base_path = os.getenv("ROOT_PATH", "/intelligent-triage")
        
        # TTS provider configuration
        self.tts_provider = os.getenv("TTS_PROVIDER", "microservice").lower()
        
        # Murf configuration
        self.murf_api_key = os.getenv("MURF_API_KEY")
        self.murf_voice_id = os.getenv("MURF_VOICE_ID", "en-IN-priya")
        self.murf_client = None
        
        # Initialize Murf client if needed
        if self.tts_provider == "murf" and MURF_AVAILABLE and self.murf_api_key:
            try:
                self.murf_client = Murf(api_key=self.murf_api_key)
                logger.info("Murf TTS client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Murf client: {e}")
                self.murf_client = None
        
        logger.info(f"TTS Provider: {self.tts_provider}")
        
    def text_to_speech(self, text: str, voice: str = "female") -> Optional[str]:
        """
        Convert text to speech using the configured TTS provider
        
        Args:
            text: Text to convert to speech
            voice: Voice type (default: "female")
            
        Returns:
            Audio URL from TTS service or None if failed
        """
        if self.tts_provider == "murf":
            return self._murf_text_to_speech(text, voice)
        else:
            return self._microservice_text_to_speech(text, voice)
    
    def _microservice_text_to_speech(self, text: str, voice: str = "female") -> Optional[str]:
        """
        Convert text to speech using the TTS microservice
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
                    logger.info(f"Microservice TTS audio URL received: {audio_url}")
                    # Transform HTTP URL to HTTPS proxy URL
                    if audio_url.startswith("http://106.201.228.100:9003/static/"):
                        # Extract the path after /static/
                        static_path = audio_url.replace("http://106.201.228.100:9003/static/", "")
                        # Build the proxy URL
                        proxy_url = f"{self.proxy_domain}{self.proxy_base_path}/static/{static_path}"
                        logger.info(f"Transformed URL: {audio_url} -> {proxy_url}")
                        return proxy_url
                    else:
                        # Return original URL if it doesn't match expected pattern
                        logger.warning(f"Unexpected TTS URL format: {audio_url}")
                        return audio_url
                else:
                    logger.error(f"No audio_url in microservice TTS response: {response_data}")
                    return None
            else:
                logger.error(f"Microservice TTS error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Microservice TTS connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Microservice TTS client error: {e}")
            return None
    
    def _murf_text_to_speech(self, text: str, voice: str = "female") -> Optional[str]:
        """
        Convert text to speech using Murf API
        """
        if not self.murf_client:
            logger.error("Murf client not initialized")
            return None
            
        try:
            # Use the configured voice ID or map the voice parameter
            voice_id = self.murf_voice_id
            if voice == "male":
                # You can add more voice mappings here
                voice_id = os.getenv("MURF_MALE_VOICE_ID", self.murf_voice_id)
            
            logger.info(f"Generating Murf TTS for text: '{text[:50]}...' with voice: {voice_id}")
            
            # Generate speech using Murf
            res = self.murf_client.text_to_speech.generate(
                text=text,
                voice_id=voice_id
            )
            
            if hasattr(res, 'audio_file') and res.audio_file:
                logger.info(f"Murf TTS audio URL received: {res.audio_file}")
                return res.audio_file
            else:
                logger.error("No audio_file in Murf response")
                return None
                
        except Exception as e:
            logger.error(f"Murf TTS error: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if the configured TTS service is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        if self.tts_provider == "murf":
            return self._murf_health_check()
        else:
            return self._microservice_health_check()
    
    def _microservice_health_check(self) -> bool:
        """Check microservice health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _murf_health_check(self) -> bool:
        """Check Murf API health"""
        return self.murf_client is not None
    
    def get_provider_info(self) -> dict:
        """Get information about the current TTS provider"""
        return {
            "provider": self.tts_provider,
            "microservice_url": self.base_url if self.tts_provider == "microservice" else None,
            "murf_voice_id": self.murf_voice_id if self.tts_provider == "murf" else None,
            "murf_available": MURF_AVAILABLE,
            "murf_client_ready": self.murf_client is not None
        }

# Global TTS client instance
tts_client = TTSClient()