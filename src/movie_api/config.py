"""
Configuration management for the Movie API.

This module uses Pydantic's BaseSettings to load and validate
configuration variables from environment variables and .env files.
Provides a single, typed `settings` object for use throughout the app.
"""

from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines the application's configuration settings."""

    tmdb_api_key: str
    cache_duration_hours: int = 1
    cache_filepath: str = ".data/cache.json"
    favorites_filepath: str = ".data/favorites.json"
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cache_duration(self) -> timedelta:
        """Returns the cache duration as a timedelta object for easy comparisons."""
        return timedelta(hours=self.cache_duration_hours)


settings = Settings()  # type: ignore[call-arg]
