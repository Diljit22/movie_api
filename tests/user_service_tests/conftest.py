# tests/user_service_tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from user_service.src.user_api.database import Base
from user_service.src.user_api.dependencies import get_db

# Use absolute imports
from user_service.src.user_api.main import app as user_app

# --- Test Database Setup ---
# Use an in-memory SQLite database for fast, isolated tests.
# The StaticPool is crucial for ensuring the same connection is used across threads
# in the test client, solving the "no such table" issue permanently.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture to create a new database for each test function.
    It creates tables, yields a session, and then drops the tables.
    """
    # Create all tables in the in-memory database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables to ensure test isolation
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture that provides a TestClient for the API, with the database
    dependency overridden to use the temporary test database.
    """

    def override_get_db():
        """Dependency override function."""
        yield db_session

    # Apply the dependency override before creating the client
    user_app.dependency_overrides[get_db] = override_get_db

    with TestClient(user_app) as c:
        yield c

    # Clean up the override after the test is done
    user_app.dependency_overrides.pop(get_db, None)


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
