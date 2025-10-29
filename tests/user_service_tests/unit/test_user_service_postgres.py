from unittest.mock import MagicMock, patch

import pytest

# Create a fake DB session object
mock_db_session = MagicMock()

# Create a fake User model instance that the crud functions will return
fake_user_model = MagicMock()
fake_user_model.id = 1
fake_user_model.username = "testuser"
fake_user_model.email = "test@example.com"
fake_user_model.hashed_password = "hashed_password_string"


@pytest.fixture(autouse=True)
def patch_crud_and_security():
    """
    Pytest fixture that automatically mocks the crud and security modules
    for all tests in this file. This isolates the service layer.
    """
    with (
        patch(
            "user_service.src.user_api.services.user_service_postgres.crud"
        ) as mock_crud,
        patch(
            "user_service.src.user_api.services.user_service_postgres.security"
        ) as mock_security,
    ):
        # Configure the mocks to return predictable values
        mock_crud.get_user_by_id.return_value = fake_user_model
        mock_crud.get_user_by_email.return_value = fake_user_model
        mock_crud.create_user.return_value = fake_user_model
        mock_security.hash_password.return_value = "a-new-hashed-password"

        yield mock_crud, mock_security


def test_get_user_by_id(patch_crud_and_security):
    """
    Tests that the service correctly calls crud.get_user_by_id.
    """
    from user_service.src.user_api.services.user_service_postgres import (
        PostgresUserService,
    )

    mock_crud, _ = patch_crud_and_security

    service = PostgresUserService(db=mock_db_session)
    user = service.get_user_by_id(user_id=1)

    # Assert that the crud function was called correctly
    mock_crud.get_user_by_id.assert_called_once_with(mock_db_session, user_id=1)

    # Assert that the service returned a correctly parsed Pydantic model
    assert user is not None
    assert user.id == 1
    assert user.email == "test@example.com"


def test_get_user_by_id_not_found(patch_crud_and_security):
    """
    Tests that the service returns None when the user is not found in the DB.
    """
    from user_service.src.user_api.services.user_service_postgres import (
        PostgresUserService,
    )

    mock_crud, _ = patch_crud_and_security

    # Configure the mock to simulate a "not found" scenario
    mock_crud.get_user_by_id.return_value = None

    service = PostgresUserService(db=mock_db_session)
    user = service.get_user_by_id(user_id=999)

    # Assert that the service correctly returns None
    assert user is None


def test_create_user(patch_crud_and_security):
    """
    Tests that the service correctly hashes the password and calls crud.create_user.
    """
    from user_service.src.user_api.schemas import UserCreate
    from user_service.src.user_api.services.user_service_postgres import (
        PostgresUserService,
    )

    mock_crud, mock_security = patch_crud_and_security

    service = PostgresUserService(db=mock_db_session)
    user_data = UserCreate(
        username="newuser", email="new@example.com", password="password123"
    )

    new_user = service.create_user(user_data)

    # Assert that the password was sent to the hashing function
    mock_security.hash_password.assert_called_once_with("password123")

    # Assert that the crud create function was called with the user data and the *newly hashed* password
    mock_crud.create_user.assert_called_once_with(
        mock_db_session, user=user_data, hashed_password="a-new-hashed-password"
    )

    # Assert the returned user is correct
    assert (
        new_user.username == "testuser"
    )  # Corresponds to the fake_user_model returned by the mock
