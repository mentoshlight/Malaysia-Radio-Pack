"""Application configuration using Pydantic Settings."""

from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://mrp:mrp@localhost:5432/mrp"
    REDIS_URL: str = "redis://localhost:6379/0"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings()
