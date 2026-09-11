"""
Centralized application settings, loaded from environment variables.
See .env.example at the project root for the full list of variables.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "change-me-in-env"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+psycopg2://skillmatch:skillmatch@db:5432/skillmatch"
    redis_url: str = "redis://redis:6379/0"

    cors_origins: List[str] = ["http://localhost:5173"]

    demo_mode: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
