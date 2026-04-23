"""Application settings loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the IRMS API."""

    database_url: str
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()  # type: ignore[call-arg]
