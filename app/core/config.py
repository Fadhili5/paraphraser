# app/core/config.py
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # silently drop unknown .env keys
    )

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
    HF_API_KEY: str | None = None

    # Rate limiting
    RATE_LIMIT: int = 100  # Requests per minute

    # Google
    GOOGLE_CLIENT_ID: str | None = None

    # Resend
    RESEND_API_KEY: str | None = None

    # Anthropic
    ANTHROPIC_API_KEY: str | None = None

    # Recaptcha
    RECAPTCHA_SECRET: str | None = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()