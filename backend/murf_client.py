import os
import logging
import time
from typing import Optional, List, Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class MurfTTSEngineError(Exception):
    """Custom exception for Murf TTS engine errors."""
    pass

class MurfClient:
    """
    Murf TTS Client for cloud-based text-to-speech generation using Murf SDK.
    """

    def __init__(self):
        self._api_key = settings.MURF_API_KEY
        self._client = None
        self._is_initialized = False
        self._available_voices = ["en-IN-priya"] # Default fallback
        self.initialize()

    def initialize(self) -> None:
        """
        Initialize the Murf TTS engine.
        """
        try:
            if not self._api_key:
                logger.warning("Murf API key not provided. TTS will fail.")
                return

            logger.info("Initializing Murf TTS engine...")

            try:
                from murf import Murf
                self._client = Murf(api_key=self._api_key)
                logger.info("Murf client initialized successfully")
                self._is_initialized = True
            except ImportError:
                logger.error("Murf SDK not installed. Please install 'murf-api'.")
                self._client = None
            except Exception as e:
                logger.error(f"Failed to initialize Murf client: {e}")
                self._client = None

        except Exception as e:
            logger.error(f"Failed to initialize Murf TTS engine: {e}")

    def text_to_speech(self, text: str, voice: str = "en-IN-priya") -> Optional[str]:
        """
        Synthesize speech from text using Murf API.

        Args:
            text: Text to synthesize
            voice: Voice ID (defaults to en-IN-priya)

        Returns:
            URL to the generated audio file or None if failed
        """
        if not self._is_initialized:
            logger.error("Murf TTS engine not initialized")
            return None

        if not text.strip():
            logger.error("Text cannot be empty")
            return None

        try:
            # Use provided voice or default
            voice_id = voice if voice else "en-IN-priya"

            logger.info(f"Synthesizing text with Murf API: '{text[:50]}...' using voice: {voice_id}")

            if self._client:
                audio_url = self._generate_speech_with_sdk(text, voice_id)
                logger.info(f"Murf API returned audio URL: {audio_url}")
                return audio_url
            else:
                logger.error("Murf SDK not available")
                return None

        except Exception as e:
            logger.error(f"Murf speech synthesis failed: {e}")
            return None

    def _generate_speech_with_sdk(self, text: str, voice_id: str) -> str:
        """
        Generate speech using Murf SDK.
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                res = self._client.text_to_speech.generate(
                    text=text,
                    voice_id=voice_id
                )

                # Extract audio URL from response
                # Assuming res.audio_file is the correct attribute based on user snippet
                audio_url = res.audio_file
                return audio_url

            except Exception as e:
                logger.error(f"Murf SDK call failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    raise MurfTTSEngineError(f"Murf SDK call failed after {max_retries} attempts: {e}")

                time.sleep(retry_delay)
                retry_delay *= 2

    def health_check(self) -> bool:
        """
        Check if the Murf TTS engine is ready for use.
        """
        return self._is_initialized and bool(self._api_key)

# Global Murf client instance
murf_client = MurfClient()