from fastapi.testclient import TestClient


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


def test_favorites_flow(client: TestClient, auth_headers: dict):
    """Tests the full lifecycle of managing favorites for an authenticated user."""
    movie_id = 550  # Fight Club

    response = client.get("/api/favorites/", headers=auth_headers)
    assert response.status_code == 200
    # The default response for an empty list of IDs is {"favorites": []}
    assert response.json()["favorites"] == []

    # 4. Add a favorite
    response = client.post(f"/api/favorites/{movie_id}", headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["movie_id"] == movie_id

    # 5. Check if it's a favorite
    response = client.get(
        f"/api/favorites/{movie_id}/is-favorite", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True

    # 6. Remove the favorite
    response = client.delete(f"/api/favorites/{movie_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["movie_id"] == movie_id

    # 7. Check again, should not be a favorite
    response = client.get(
        f"/api/favorites/{movie_id}/is-favorite", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False
