"""
Configuration management for the User API.
"""

import secrets
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines the User Service's configuration settings."""

    # Should match the DATABASE_URL in your .env file for docker-compose
    database_url: str = "postgresql://user:password@postgres:5432/movie_db"

    favorites_implementation: Literal["json_file", "in_memory"] = "json_file"
    user_implementation: Literal["postgres", "in_memory"] = "postgres"

    favorites_filepath: str = ".data/favorites.json"

    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # Tokens will be valid for 30 minutes

    movie_service_url: str = "http://movie_service:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
