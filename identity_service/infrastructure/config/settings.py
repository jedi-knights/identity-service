"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Identity Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://identity:identity@localhost:5432/identity",
        alias="DATABASE_URL",
    )
    db_echo: bool = False

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # JWT
    jwt_algorithm: str = "RS256"
    jwt_issuer: str = "identity-service"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # Security
    jwt_private_key: Optional[str] = None
    jwt_public_key: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
