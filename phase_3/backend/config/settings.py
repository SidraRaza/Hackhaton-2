from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    neon_database_url: Optional[str] = os.getenv("NEON_DATABASE_URL")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    next_public_api_url: str = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"

settings = Settings()