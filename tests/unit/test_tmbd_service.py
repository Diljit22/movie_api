"""
Unit tests for the TMDBService.
"""

import re

import pytest
from fastapi import HTTPException

from movie_service.src.movie_api.services.tmdb import TMDBService


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_get_trending_movies_success(httpx_mock):
    """Tests a successful API call to fetch trending movies."""
    mock_response_data = {
        "page": 1,
        "results": [
            {"id": 1, "title": "Test Movie", "poster_path": "/test.jpg"},
            {"id": 2, "title": "Another Movie", "poster_path": "/another.jpg"},
        ],
        "total_pages": 1,
        "total_results": 2,
    }
    url_pattern = re.compile(r".*/trending/movie/day.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response_data)

    service = TMDBService()
    result = await service.get_trending_movies(time_window="day")

    # Verify poster paths were transformed
    expected_path = "https://image.tmdb.org/t/p/w500/test.jpg"
    assert result["results"][0]["poster_path"] == expected_path
    assert result["results"][0]["id"] == 1
    assert result["results"][0]["title"] == "Test Movie"
    
    # Verify multiple results
    assert len(result["results"]) == 2


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_get_trending_movies_week(httpx_mock):
    """Tests fetching weekly trending movies."""
    mock_response_data = {
        "page": 1,
        "results": [{"id": 3, "title": "Weekly Movie", "poster_path": "/weekly.jpg"}],
        "total_pages": 1,
        "total_results": 1,
    }
    url_pattern = re.compile(r".*/trending/movie/week.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response_data)

    service = TMDBService()
    result = await service.get_trending_movies(time_window="week")

    assert result["results"][0]["id"] == 3
    assert result["results"][0]["title"] == "Weekly Movie"


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_get_movie_details_success(httpx_mock):
    """Tests a successful API call to fetch movie details."""
    mock_response = {
        "id": 550,
        "title": "Fight Club",
        "overview": "An insomniac office worker...",
        "poster_path": "/fight_club.jpg",
        "release_date": "1999-10-15",
        "tagline": "Mischief. Mayhem. Soap.",
        "status": "Released",
        "vote_average": 8.4,
        "vote_count": 25000,
    }
    url_pattern = re.compile(r".*/movie/550.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response)

    service = TMDBService()
    result = await service.get_movie_details(movie_id=550)

    assert result["id"] == 550
    assert result["title"] == "Fight Club"
    assert result["poster_path"] == "https://image.tmdb.org/t/p/w500/fight_club.jpg"


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_get_movie_details_not_found(httpx_mock):
    """Tests that a 404 from the TMDB API raises an HTTPException."""
    url_pattern = re.compile(r".*/movie/99999.*")
    httpx_mock.add_response(url=url_pattern, status_code=404)

    service = TMDBService()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_movie_details(movie_id=99999)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_search_movies_success(httpx_mock):
    """Tests a successful movie search."""
    mock_response = {
        "page": 1,
        "results": [
            {"id": 603, "title": "The Matrix", "poster_path": "/matrix.jpg"},
            {"id": 604, "title": "The Matrix Reloaded", "poster_path": "/reloaded.jpg"},
        ],
        "total_pages": 1,
        "total_results": 2,
    }
    url_pattern = re.compile(r".*/search/movie.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response)

    service = TMDBService()
    result = await service.search_movies(query="matrix")

    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "The Matrix"
    assert "image.tmdb.org" in result["results"][0]["poster_path"]


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_search_movies_no_results(httpx_mock):
    """Tests search with no results."""
    mock_response = {
        "page": 1,
        "results": [],
        "total_pages": 0,
        "total_results": 0,
    }
    url_pattern = re.compile(r".*/search/movie.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response)

    service = TMDBService()
    result = await service.search_movies(query="nonexistentmovie12345")

    assert result["results"] == []
    assert result["total_results"] == 0


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_tmdb_api_server_error(httpx_mock):
    """Tests that a 5xx error from the TMDB API raises an HTTPException."""
    url_pattern = re.compile(r".*/trending/movie/day.*")
    httpx_mock.add_response(url=url_pattern, status_code=503)

    service = TMDBService()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_trending_movies(time_window="day")

    assert exc_info.value.status_code == 503


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_tmdb_network_error(httpx_mock):
    """Test handling of network timeouts."""
    import httpx

    url_pattern = re.compile(r".*/trending/movie/day.*")
    httpx_mock.add_exception(httpx.TimeoutException("Timeout"), url=url_pattern)

    service = TMDBService()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_trending_movies(time_window="day")

    assert exc_info.value.status_code == 503
    assert "communicating" in exc_info.value.detail.lower()


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_tmdb_connection_error(httpx_mock):
    """Test handling of connection errors."""
    import httpx

    url_pattern = re.compile(r".*/movie/550.*")
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"), url=url_pattern)

    service = TMDBService()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_movie_details(movie_id=550)

    assert exc_info.value.status_code == 503


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_poster_path_transformation_with_none(httpx_mock):
    """Tests that None poster_path doesn't cause errors."""
    mock_response = {
        "id": 123,
        "title": "Movie Without Poster",
        "poster_path": None,  # No poster available
        "release_date": "2024-01-01",
    }
    url_pattern = re.compile(r".*/movie/123.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response)

    service = TMDBService()
    result = await service.get_movie_details(movie_id=123)

    # poster_path should remain None, not cause an error
    assert result["poster_path"] is None


@pytest.mark.httpx
@pytest.mark.asyncio
async def test_tmdb_401_unauthorized(httpx_mock):
    """Tests handling of unauthorized errors (invalid API key)."""
    url_pattern = re.compile(r".*/trending/movie/day.*")
    httpx_mock.add_response(url=url_pattern, status_code=401)

    service = TMDBService()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_trending_movies(time_window="day")

    assert exc_info.value.status_code == 401