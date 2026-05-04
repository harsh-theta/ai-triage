import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    MURF_API_KEY: str = os.getenv("MURF_API_KEY", "")
    ROOT_PATH: str = os.getenv("ROOT_PATH", "/intelligent-triage")

settings = Settings()