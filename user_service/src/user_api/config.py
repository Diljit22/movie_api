"""
Configuration management for the User API.
"""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Defines the User Service's configuration settings."""

    # Should match the DATABASE_URL in your .env file for docker-compose
    database_url: str = "postgresql://user:password@postgres:5432/movie_db"

    favorites_implementation: Literal["json_file", "in_memory"] = "json_file"
    user_implementation: Literal["postgres", "in_memory"] = "postgres"

    favorites_filepath: str = ".data/favorites.json"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()