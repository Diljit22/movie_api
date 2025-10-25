"""
Shared pytest fixtures for the entire test suite.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from movie_service.src.movie_api.dependencies import (
    get_distributed_cache,
    get_in_memory_cache,
    get_movie_service,
)
from movie_service.src.movie_api.interfaces import CacheInterface, MovieServiceInterface
from movie_service.src.movie_api.main import app
from movie_service.src.movie_api.monitoring.cache_stats import cache_stats

# --- Mock Services for Testing ---

class MockCache(CacheInterface):
    """Simple in-memory mock cache for testing."""
    def __init__(self):
        self._cache = {}

    async def get(self, key: str):
        return self._cache.get(key)

    async def set(self, key: str, data):
        self._cache[key] = data

class MockMovieService(MovieServiceInterface):
    """
    Mock movie service that returns hardcoded data and tracks API calls.
    """
    def __init__(self):
        self.calls_to_trending = 0
        self.calls_to_details = 0
        self.calls_to_search = 0

    async def get_trending_movies(self, time_window: str):
        self.calls_to_trending += 1
        return {
            "page": 1, "total_pages": 1, "total_results": 1,
            "results": [{
                "id": 1, "title": "Mock Trending Movie", "overview": "A mock movie",
                "poster_path": "/mock.jpg", "release_date": "2024-01-01",
            }],
        }

    async def get_movie_details(self, movie_id: int):
        self.calls_to_details += 1
        if movie_id == 99999:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {
            "id": movie_id, "title": f"Mock Movie {movie_id}", "overview": "A mock movie",
            "poster_path": "/mock.jpg", "release_date": "2024-01-01",
            "tagline": "Mock tagline", "status": "Released",
            "vote_average": 8.5, "vote_count": 1000,
        }

    async def search_movies(self, query: str):
        self.calls_to_search += 1
        return {
            "page": 1, "total_pages": 1, "total_results": 1,
            "results": [{
                "id": 2, "title": f"Search Result for {query}", "overview": "A mock movie",
                "poster_path": "/mock.jpg", "release_date": "2024-01-01",
            }],
        }

# --- Pytest Fixtures ---

@pytest.fixture(scope="function")
def client_with_mocks():
    """
    Provides a TestClient with all dependencies overridden by mocks.
    Resets mocks and stats for each test function to ensure isolation.

    Yields:
        tuple: (client, l1_cache, l2_cache, movie_service)
    """
    mock_l1_cache = MockCache()
    mock_l2_cache = MockCache()
    mock_movie_service = MockMovieService()

    # Reset custom stats before each test run
    cache_stats.reset()

    app.dependency_overrides[get_in_memory_cache] = lambda: mock_l1_cache
    app.dependency_overrides[get_distributed_cache] = lambda: mock_l2_cache
    app.dependency_overrides[get_movie_service] = lambda: mock_movie_service

    with TestClient(app) as client:
        yield client, mock_l1_cache, mock_l2_cache, mock_movie_service

    # Teardown: Clear dependency overrides after each test
    app.dependency_overrides = {}