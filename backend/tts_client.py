import requests
import os
from typing import Optional, Dict, Any
import uuid
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Simple circuit breaker to prevent repeated calls to failing services"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if we can execute the operation"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record a successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"

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
        
        # Retry configuration
        self.max_retries = int(os.getenv("TTS_MAX_RETRIES", "2"))
        self.retry_delay = float(os.getenv("TTS_RETRY_DELAY", "1.0"))
        
        # Circuit breakers for each provider
        self.microservice_circuit_breaker = CircuitBreaker(
            failure_threshold=int(os.getenv("TTS_CIRCUIT_BREAKER_THRESHOLD", "5")),
            recovery_timeout=int(os.getenv("TTS_CIRCUIT_BREAKER_TIMEOUT", "60"))
        )
        self.murf_circuit_breaker = CircuitBreaker(
            failure_threshold=int(os.getenv("TTS_CIRCUIT_BREAKER_THRESHOLD", "5")),
            recovery_timeout=int(os.getenv("TTS_CIRCUIT_BREAKER_TIMEOUT", "60"))
        )
        
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
        logger.info(f"TTS Max Retries: {self.max_retries}, Retry Delay: {self.retry_delay}s")
        
    def text_to_speech(self, text: str, voice: str = "female") -> Optional[str]:
        """
        Convert text to speech using the configured TTS provider with retry logic and circuit breaker
        
        Args:
            text: Text to convert to speech
            voice: Voice type (default: "female")
            
        Returns:
            Audio URL from TTS service or None if failed
        """
        # Get the appropriate circuit breaker
        circuit_breaker = (self.murf_circuit_breaker if self.tts_provider == "murf" 
                          else self.microservice_circuit_breaker)
        
        # Check circuit breaker before attempting
        if not circuit_breaker.can_execute():
            logger.warning(f"TTS circuit breaker is OPEN for {self.tts_provider}, skipping TTS generation")
            return None
        
        # Attempt TTS with retry logic
        for attempt in range(self.max_retries + 1):
            try:
                if self.tts_provider == "murf":
                    result = self._murf_text_to_speech_internal(text, voice)
                else:
                    result = self._microservice_text_to_speech_internal(text, voice)
                
                if result:
                    # Success - record it and return
                    circuit_breaker.record_success()
                    logger.info(f"TTS successful on attempt {attempt + 1}")
                    return result
                else:
                    # Failed but no exception - could be rate limit or service issue
                    logger.warning(f"TTS attempt {attempt + 1} failed (no result)")
                    
            except Exception as e:
                logger.error(f"TTS attempt {attempt + 1} failed with exception: {e}")
            
            # If not the last attempt, wait before retrying
            if attempt < self.max_retries:
                logger.info(f"Retrying TTS in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        # All attempts failed - record failure in circuit breaker
        circuit_breaker.record_failure()
        logger.error(f"TTS failed after {self.max_retries + 1} attempts, circuit breaker state: {circuit_breaker.state}")
        return None
    
    def _microservice_text_to_speech_internal(self, text: str, voice: str = "female") -> Optional[str]:
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
    
    def _murf_text_to_speech_internal(self, text: str, voice: str = "female") -> Optional[str]:
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
            "murf_client_ready": self.murf_client is not None,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }
    
    def get_circuit_breaker_status(self) -> dict:
        """Get circuit breaker status for both providers"""
        return {
            "microservice": {
                "state": self.microservice_circuit_breaker.state,
                "failure_count": self.microservice_circuit_breaker.failure_count,
                "last_failure_time": self.microservice_circuit_breaker.last_failure_time.isoformat() if self.microservice_circuit_breaker.last_failure_time else None,
                "failure_threshold": self.microservice_circuit_breaker.failure_threshold,
                "recovery_timeout": self.microservice_circuit_breaker.recovery_timeout
            },
            "murf": {
                "state": self.murf_circuit_breaker.state,
                "failure_count": self.murf_circuit_breaker.failure_count,
                "last_failure_time": self.murf_circuit_breaker.last_failure_time.isoformat() if self.murf_circuit_breaker.last_failure_time else None,
                "failure_threshold": self.murf_circuit_breaker.failure_threshold,
                "recovery_timeout": self.murf_circuit_breaker.recovery_timeout
            }
        }

# Global TTS client instance
tts_client = TTSClient()