import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from user_service.src.user_api.database import Base
from user_service.src.user_api.dependencies import get_db

from user_service.src.user_api.main import app as user_app

# Use an in-memory SQLite database for fast, isolated tests.
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
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
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

    user_app.dependency_overrides[get_db] = override_get_db

    with TestClient(user_app) as c:
        yield c

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
