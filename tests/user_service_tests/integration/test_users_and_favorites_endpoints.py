import pytest
from fastapi.testclient import TestClient
from pytest_httpx import HTTPXMock


def test_create_user_and_get_profile(client: TestClient):
    """Tests user creation and profile retrieval."""
    # Create user
    response = client.post(
        "/api/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test@example.com"
    assert user_data["username"] == "testuser"
    assert "id" in user_data

    user_id = user_data["id"]

    # Get user profile
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data["id"] == user_id
    assert profile_data["email"] == "test@example.com"


def test_create_user_duplicate_email(client: TestClient):
    """Tests that creating a user with a duplicate email fails."""
    client.post(
        "/api/users/",
        json={
            "username": "testuser1",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    # Second attempt with the same email
    response = client.post(
        "/api/users/",
        json={
            "username": "testuser2",
            "email": "duplicate@example.com",
            "password": "password456",
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]["message"]


# This test file requires an authenticated user, so we need a helper to log in.
# It will be used in the auth tests as well.
def get_auth_headers(client: TestClient, email: str, password: str) -> dict:
    """Helper function to log in and get JWT auth headers."""
    response = client.post("/api/login", data={"username": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.httpx
def test_favorites_flow(client: TestClient, auth_headers: dict, httpx_mock: HTTPXMock):
    """Tests the full lifecycle of managing favorites for an authenticated user."""
    movie_id = 550  # Fight Club

    # When the user_service calls the movie_service, intercept it and return this fake data.
    mock_movie_service_url = "http://movie_service:8000/api/movies/batch"
    httpx_mock.add_response(
        url=mock_movie_service_url,
        method="POST",
        json={
            "movies": [
                {
                    "id": movie_id,
                    "title": "Fight Club",
                    "overview": "A ticking-time-bomb insomniac...",
                    "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                    "release_date": "1999-10-15",
                }
            ],
            "total_requested": 1,
            "total_found": 1,
            "errors": None,
        },
    )

    # 1. Get initial list of favorites (calls the mock)
    response = client.get("/api/favorites/", headers=auth_headers)
    assert response.status_code == 200
    # The initial list of favorite IDs is empty, so the service won't call the mock.
    assert response.json()["favorites"] == []

    # 2. Add a favorite
    response = client.post(f"/api/favorites/{movie_id}", headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["movie_id"] == movie_id

    # 3. Check if it's a favorite
    response = client.get(
        f"/api/favorites/{movie_id}/is-favorite", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True

    # 4. Get the list of favorites again to confirm the mock is working
    response = client.get("/api/favorites/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["favorites"]) == 1
    assert response.json()["favorites"][0]["id"] == movie_id

    # 5. Remove the favorite
    response = client.delete(f"/api/favorites/{movie_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["movie_id"] == movie_id

    # 6. Check again, should not be a favorite
    response = client.get(
        f"/api/favorites/{movie_id}/is-favorite", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False
