"""
Integration tests for the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from movie_api.dependencies import (
    get_cache,
    get_favorites_service,
    get_movie_service,
)
from movie_api.interfaces import (
    CacheInterface,
    FavoritesInterface,
    MovieServiceInterface,
)
from movie_api.main import app

# Fake Services


class FakeCache(CacheInterface):
    """Simple in-memory fake cache."""

    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, data):
        self._cache[key] = data


class FakeMovieService(MovieServiceInterface):
    """Movie service that returns hardcoded data and tracks calls."""

    def __init__(self):
        self.calls_to_trending = 0

    async def get_trending_movies(self, time_window: str):
        self.calls_to_trending += 1
        return {
            "page": 1,
            "results": [
                {
                    "id": 1,
                    "title": "Fake Trending Movie",
                    "overview": "...",
                    "poster_path": "https://image.tmdb.org/t/p/w500/fake_path.jpg",
                    "release_date": "",
                }
            ],
            "total_pages": 1,
            "total_results": 1,
        }

    async def get_movie_details(self, movie_id: int):
        return {
            "id": movie_id,
            "title": "Fake Movie Detail",
            "overview": "...",
            "poster_path": "",
            "release_date": "",
            "tagline": "",
            "status": "",
            "vote_average": 0.0,
            "vote_count": 0,
        }


class FakeFavorites(FavoritesInterface):
    """Simple in-memory fake favorites list."""

    def __init__(self):
        self._favs = []

    def add(self, movie_id):
        self._favs.append(movie_id)

    def remove(self, movie_id):
        self._favs.remove(movie_id)

    def get_all(self):
        return self._favs

    def is_favorite(self, movie_id):
        return movie_id in self._favs


# Pytest Fixtures


@pytest.fixture
def client_with_fakes():
    """Provides TestClient with all dependencies overridden by fakes."""
    fake_cache = FakeCache()
    fake_movie_service = FakeMovieService()
    fake_favorites = FakeFavorites()

    app.dependency_overrides[get_cache] = lambda: fake_cache
    app.dependency_overrides[get_movie_service] = lambda: fake_movie_service
    app.dependency_overrides[get_favorites_service] = lambda: fake_favorites

    with TestClient(app) as client:
        # Yield the client and the fakes
        yield client, fake_cache, fake_movie_service, fake_favorites

    # Teardown
    app.dependency_overrides = {}


# Integration Tests


def test_get_trending_uses_cache(client_with_fakes):
    """Tests that the /api/trending endpoint uses the cache on the second call."""
    client, cache, movie_service, _ = client_with_fakes

    # First call hits service (day)
    response1 = client.get("/api/trending/day")
    assert response1.status_code == 200
    assert movie_service.calls_to_trending == 1

    # Second call hits the cache
    response2 = client.get("/api/trending/day")
    assert response2.status_code == 200
    # Verify service was not called again
    assert movie_service.calls_to_trending == 1

    # First call hits service (week)
    response1 = client.get("/api/trending/week")
    assert response1.status_code == 200
    assert movie_service.calls_to_trending == 2

    # Second call hits the cache
    response2 = client.get("/api/trending/week")
    assert response2.status_code == 200
    # Verify service was not called again
    assert movie_service.calls_to_trending == 2


def test_favorites_lifecycle(client_with_fakes):
    """Tests the full add -> check -> get all -> remove -> check lifecycle for favorites."""
    client, _, _, _ = client_with_fakes

    # Initially, movie 789 is not a favorite
    response = client.get("/api/favorites/789/is-favorite")
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False

    # Add movie 789 to favorites
    response = client.post("/api/favorites/789")
    assert response.status_code == 201

    # Verify it is now a favorite
    response = client.get("/api/favorites/789/is-favorite")
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True

    # Get all favorites and check
    response = client.get("/api/favorites/")
    assert response.status_code == 200
    assert response.json()["favorites"] == [789]

    # Remove the favorite
    response = client.delete("/api/favorites/789")
    assert response.status_code == 200

    # Verify no longer a favorite
    response = client.get("/api/favorites/789/is-favorite")
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False


def test_trending_movies_empty_results(client_with_fakes):
    """Test handling of empty movie list."""
    client, _, movie_service, _ = client_with_fakes

    # Override to return empty results
    async def empty_trending(time_window: str):
        return {"page": 1, "results": [], "total_pages": 0, "total_results": 0}

    movie_service.get_trending_movies = empty_trending

    response = client.get("/api/trending/day")
    assert response.status_code == 200
    assert response.json()["results"] == []
