from fastapi.testclient import TestClient


def test_login_success(client: TestClient):
    """Tests successful login and token generation."""
    email = "login_success@example.com"
    password = "a-secure-password"
    client.post(
        "/api/users/",
        json={"username": "login_user", "email": email, "password": password},
    )
    response = client.post("/api/login", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure_wrong_password(client: TestClient):
    """Tests login failure with an incorrect password."""
    email = "wrong_pass@example.com"
    password = "a-secure-password"
    client.post(
        "/api/users/",
        json={"username": "wrong_pass_user", "email": email, "password": password},
    )

    response = client.post(
        "/api/login", data={"username": email, "password": "this-is-wrong"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]["message"]


def test_get_me_endpoint(client: TestClient, auth_headers: dict):
    """Tests the protected /api/users/me endpoint."""
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # The user created by the fixture is "auth_user" with "auth_test@example.com"
    assert data["email"] == "auth_test@example.com"
    assert "id" in data


def test_update_me_endpoint(client: TestClient, auth_headers: dict):
    """Tests updating the current user's profile."""
    response = client.put(
        "/api/users/me", headers=auth_headers, json={"username": "updated_auth_user"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updated_auth_user"
