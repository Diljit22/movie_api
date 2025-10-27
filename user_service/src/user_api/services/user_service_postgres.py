"""
Postgres implementation of the UserServiceInterface.
"""
from sqlalchemy.orm import Session

from user_service.src.user_api import crud, schemas, security
from user_service.src.user_api.interfaces import UserServiceInterface


class PostgresUserService(UserServiceInterface):
    """
    Service layer for user management that interacts with a Postgres database.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> schemas.User | None:
        """Retrieves a user by their ID from the database."""
        db_user = crud.get_user_by_id(self.db, user_id=user_id)
        return schemas.User.model_validate(db_user) if db_user else None

    def get_user_by_email(self, email: str) -> schemas.User | None:
        """Retrieves a user by their email from the database."""
        db_user = crud.get_user_by_email(self.db, email=email)
        return schemas.User.model_validate(db_user) if db_user else None

    def create_user(self, user_data: schemas.UserCreate) -> schemas.User:
        """
        Hashes the user's password and creates a new user in the database.
        """
        hashed_password = security.hash_password(user_data.password)
        db_user = crud.create_user(
            self.db, user=user_data, hashed_password=hashed_password
        )
        return schemas.User.model_validate(db_user)