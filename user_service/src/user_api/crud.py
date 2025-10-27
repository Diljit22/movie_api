"""
CRUD operations for interacting with the database models.
"""
from sqlalchemy.orm import Session

from user_service.src.user_api import models, schemas


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Fetches a user by their primary key ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Fetches a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    """
    Creates a new user record in the database.
    Note: It expects the password to be already hashed.
    """
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user