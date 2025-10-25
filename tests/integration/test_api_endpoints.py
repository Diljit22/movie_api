"""
Integration tests for the Movie API endpoints.

These tests verify the behavior of the API, including routing,
dependency injection, caching logic, and error handling.
"""

class TestBasicEndpoints:
    def test_root_endpoint(self, client_with_mocks):
        """Test the root endpoint returns a successful response."""
        client, _, _, _ = client_with_mocks
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_endpoint(self, client_with_mocks):
        """Test the health check endpoint."""
        client, _, _, _ = client_with_mocks
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_metrics_endpoints(self, client_with_mocks):
        """Test metrics and metrics reset endpoints work correctly."""
        client, _, _, _ = client_with_mocks
        client.get("/api/trending/day") # Generate some stats
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.json()["cache_stats"]["api_calls"] == 1
        reset_response = client.post("/metrics/reset")
        assert reset_response.status_code == 200
        response_after_reset = client.get("/metrics")
        assert response_after_reset.json()["cache_stats"]["api_calls"] == 0

    def test_headers_are_present(self, client_with_mocks):
        """Tests that responses include X-Request-ID and X-Process-Time headers."""
        client, _, _, _ = client_with_mocks
        response = client.get("/")
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        assert float(response.headers["X-Process-Time"]) >= 0

class TestMovieApiCaching:
    def test_full_cache_miss_populates_caches(self, client_with_mocks):
        """Scenario: L1 & L2 miss -> Call API -> Populate L1 & L2."""
        client, l1_cache, l2_cache, movie_service = client_with_mocks
        response = client.get("/api/movie/101")
        assert response.status_code == 200
        assert movie_service.calls_to_details == 1
        assert "movie_details_101" in l1_cache._cache
        assert "movie_details_101" in l2_cache._cache

    def test_l1_cache_hit(self, client_with_mocks):
        """Scenario: L1 hit -> Return from L1 -> No API call."""
        client, _, _, movie_service = client_with_mocks
        client.get("/api/movie/102") # First call populates cache
        assert movie_service.calls_to_details == 1
        response = client.get("/api/movie/102") # Second call should hit L1
        assert response.status_code == 200
        assert movie_service.calls_to_details == 1 # Service not called again

    def test_l2_cache_hit_populates_l1(self, client_with_mocks):
        """Scenario: L1 miss -> L2 hit -> Populate L1 -> No API call."""
        client, l1_cache, l2_cache, movie_service = client_with_mocks
        # Manually populate L2 to simulate a previous request
        complete_movie_data = {
            "id": 103, "title": "From L2", "overview": "Cached overview",
            "poster_path": "/cached.jpg", "release_date": "2024-01-01",
            "tagline": "Cached tagline", "status": "Released",
            "vote_average": 7.7, "vote_count": 777,
        }
        l2_cache._cache["movie_details_103"] = complete_movie_data
        response = client.get("/api/movie/103")
        assert response.status_code == 200
        assert movie_service.calls_to_details == 0 # Service was not called
        assert "movie_details_103" in l1_cache._cache # L1 was populated
        assert response.json()["overview"] == "Cached overview"
        
class TestMovieApiEndpoints:
    def test_get_movie_details_not_found(self, client_with_mocks):
        """Tests 404 error handling for a non-existent movie."""
        client, _, _, _ = client_with_mocks
        response = client.get("/api/movie/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]["message"].lower()

    def test_search_movies(self, client_with_mocks):
        """Tests the search endpoint works correctly."""
        client, _, _, movie_service = client_with_mocks
        response = client.get("/api/search?query=Test")
        assert response.status_code == 200
        assert "Search Result for Test" in response.text
        assert movie_service.calls_to_search == 1

class TestBatchEndpoint:
    def test_batch_movies_success(self, client_with_mocks):
        """Tests a successful batch request for multiple movies."""
        client, _, _, _ = client_with_mocks
        response = client.post("/api/movies/batch", json={"movie_ids": [10, 20, 30]})
        assert response.status_code == 200
        data = response.json()
        assert data["total_requested"] == 3
        assert data["total_found"] == 3
        assert len(data["movies"]) == 3
        assert data["errors"] is None

    def test_batch_movies_partial_failure(self, client_with_mocks):
        """Tests a batch request where one movie is not found (404)."""
        client, _, _, _ = client_with_mocks
        response = client.post("/api/movies/batch", json={"movie_ids": [10, 99999, 30]})
        assert response.status_code == 200
        data = response.json()
        assert data["total_requested"] == 3
        assert data["total_found"] == 2
        assert len(data["movies"]) == 2
        assert len(data["errors"]) == 1
        assert data["errors"][0]["movie_id"] == 99999
        assert "not found" in data["errors"][0]["error"].lower()

    def test_batch_movies_with_duplicates(self, client_with_mocks):
        """Tests that duplicate IDs in a batch request are handled correctly."""
        client, _, _, movie_service = client_with_mocks
        response = client.post("/api/movies/batch", json={"movie_ids": [10, 20, 10]})
        assert response.status_code == 200
        data = response.json()
        assert data["total_requested"] == 2 # Only 2 unique IDs requested
        assert data["total_found"] == 2
        assert movie_service.calls_to_details == 2 # Service called once per unique ID

    def test_batch_movies_validation_empty_list(self, client_with_mocks):
        """Tests validation for an empty movie_ids list."""
        client, _, _, _ = client_with_mocks
        response = client.post("/api/movies/batch", json={"movie_ids": []})
        assert response.status_code == 422
        error_details = response.json()["detail"]
        assert isinstance(error_details, list)
        assert "at least 1 item" in error_details[0]["msg"]

    def test_batch_movies_validation_too_many_ids(self, client_with_mocks):
        """Tests validation for a list with more than 50 movie IDs."""
        client, _, _, _ = client_with_mocks
        response = client.post("/api/movies/batch", json={"movie_ids": list(range(51))})
        assert response.status_code == 422
        error_details = response.json()["detail"]
        assert isinstance(error_details, list)
        assert "at most 50 items" in error_details[0]["msg"]