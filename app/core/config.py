# app/core/config.py

from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # General
    APP_NAME: str = "AI Paraphraser"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="Full Postgres DSN, e.g. postgresql+asyncpg://user:pass@host/db"
    )

    # Auth
    SECRET_KEY: str = Field(
        ...,
        description="JWT secret for signing tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Hugging Face
    HF_API_KEY: str | None = None   # Only if using HF Inference API

    # Rate limiting (optional)
    RATE_LIMIT: int = 100  # Requests per minute

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
