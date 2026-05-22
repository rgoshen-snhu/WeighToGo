"""Application configuration loaded from the environment."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables and a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://weighttogo:weighttogo@localhost:5432/weighttogo_dev"


@lru_cache
def get_settings() -> Settings:
    """Return the application settings, constructed once and cached.

    Settings are built lazily rather than at import time so that a
    misconfigured environment surfaces where settings are first used,
    instead of crashing every module that imports this one.
    """
    return Settings()
