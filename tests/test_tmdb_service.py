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
        "results": [{"id": 1, "title": "Test Movie", "poster_path": "/test.jpg"}]
    }
    url_pattern = re.compile(r".*/trending/movie/day.*")
    httpx_mock.add_response(url=url_pattern, json=mock_response_data)

    service = TMDBService()
    result = await service.get_trending_movies(time_window="day")

    expected_path = "https://image.tmdb.org/t/p/w500/test.jpg"
    assert result["results"][0]["poster_path"] == expected_path

    assert result["results"][0]["id"] == 1
    assert result["results"][0]["title"] == "Test Movie"


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
