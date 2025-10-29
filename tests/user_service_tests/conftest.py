import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from user_service.src.user_api.database import Base
from user_service.src.user_api.dependencies import get_db
from user_service.src.user_api.main import app as user_app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client():
    """
    Pytest fixture that provides a TestClient for the user_service API.

    This fixture handles the entire setup and teardown process:
    1. Creates all database tables in a temporary in-memory SQLite DB.
    2. Overrides the `get_db` dependency to use this temporary DB.
    3. Yields a TestClient instance for making API calls.
    4. Drops all database tables after the test is complete.
    """
    # 1. Create the tables
    Base.metadata.create_all(bind=engine)

    # 2. Define the dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Apply the override
    user_app.dependency_overrides[get_db] = override_get_db

    # 3. Yield the client
    with TestClient(user_app) as c:
        yield c

    # 4. Clean up: remove the override and drop the tables
    user_app.dependency_overrides = {}
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def auth_headers(client: TestClient):
    """
    Fixture that creates a test user, logs them in, and returns
    the JWT Authorization headers.
    """
    email = "auth_test@example.com"
    password = "password123"
    client.post(
        "/api/users/",
        json={"username": "auth_user", "email": email, "password": password},
    )
    response = client.post("/api/login", data={"username": email, "password": password})
    assert response.status_code == 200, "Failed to log in during test setup"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
