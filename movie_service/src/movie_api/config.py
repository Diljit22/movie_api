"""
Configuration management for the Movie API.

Uses Pydantic's BaseSettings to load and validate configuration variables
from environment variables and .env files. Provides a single,
typed `settings` object for use throughout the app.
"""

from datetime import timedelta
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines the application's configuration settings."""

    tmdb_api_key: str
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p/w500"

    cache_duration_hours: int = 1
    cache_filepath: str = ".data/cache.json"
    cache_implementation: Literal["redis", "json_file", "in_memory"] = "redis"
    redis_url: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cache_duration(self) -> timedelta:
        """Returns the cache duration as a timedelta object for easy comparisons."""
        return timedelta(hours=self.cache_duration_hours)


settings = Settings()  # type: ignore[call-arg]
