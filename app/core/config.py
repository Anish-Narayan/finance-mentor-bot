# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    FIREBASE_PROJECT_ID: str
    WEBHOOK_URL: str
    FIREBASE_SERVICE_ACCOUNT_FILE: str = "firebase-service-account.json"
    
    class Config:
        env_file = ".env"

settings = Settings()