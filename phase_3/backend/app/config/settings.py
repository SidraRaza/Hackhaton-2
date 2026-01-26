from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str

    # Auth settings
    BETTER_AUTH_SECRET: str

    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"  # Default model

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Task management defaults
    DEFAULT_MAX_CONTEXT_MESSAGES: int = 50  # Maximum number of messages to include in context

    class Config:
        env_file = ".env"


settings = Settings()