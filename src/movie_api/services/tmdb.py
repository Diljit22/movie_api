"""
Implementation of the MovieServiceInterface using TMDB.

Provides asynch movie data fetches.
"""

import logging
from typing import cast

import httpx
from fastapi import HTTPException

from movie_api.config import settings
from movie_api.interfaces import MovieServiceInterface

BASE_URL = "https://api.themoviedb.org/3"


class TMDBService(MovieServiceInterface):
    """Service that fetches movie data from the TMDB API."""

    async def get_trending_movies(self) -> dict:
        """Get the trending movie list."""
        url = f"{BASE_URL}/trending/movie/day"
        params = {"api_key": settings.tmdb_api_key}
        return await self._make_api_request(url, params)

    async def get_movie_details(self, movie_id: int) -> dict:
        """Get movie details."""
        url = f"{BASE_URL}/movie/{movie_id}"
        params = {"api_key": settings.tmdb_api_key}
        return await self._make_api_request(url, params)

    async def _make_api_request(self, url: str, params: dict) -> dict:
        """Helper method performing async HTTP request."""
        async with httpx.AsyncClient() as client:
            try:
                logging.info(f"Making TMDB API request to: {url}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                return cast(dict, response.json())

            except httpx.RequestError as e:
                logging.error(f"Network error requesting '{e.request.url.path}': {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Error communicating with the movie database.",
                ) from e

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logging.warning(
                        f"Resource not found at '{e.request.url.path}' (404)."
                    )
                    raise HTTPException(
                        status_code=404, detail="The requested resource was not found."
                    ) from e

                logging.error(
                    f"TMDB API error for '{e.request.url.path}': {e.response.status_code}"
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail="An error occurred with the movie database.",
                ) from e
