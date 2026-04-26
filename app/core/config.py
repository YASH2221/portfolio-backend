import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    GEMINI_API_KEY: str = ""
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ADMIN_SECRET_KEY: str = "portfolio-admin-secret"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')

settings = Settings()
