"""
Dependency Injection providers.

Contains functions that FastAPI's `Depends` system will use to
create and inject instances of our service and cache classes into the
API route handlers.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from user_service.src.user_api import config, interfaces, models, schemas, security
from user_service.src.user_api.database import SessionLocal
from user_service.src.user_api.services.favorites_service_json import (
    JSONFileFavoritesService,
)
from user_service.src.user_api.services.in_memory_favorites import (
    InMemoryFavoritesService,
)
from user_service.src.user_api.services.in_memory_users import InMemoryUserService
from user_service.src.user_api.services.user_service_postgres import PostgresUserService


# --- Database Dependency ---
def get_db():
    """
    FastAPI dependency that provides a database session.
    It ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSessionDep = Annotated[Session, Depends(get_db)]


# --- Service Implementations Mapping ---
FAVORITES_IMPLEMENTATIONS: dict[
    str, Callable[[], interfaces.FavoritesServiceInterface]
] = {
    "json_file": lambda: JSONFileFavoritesService(
        filepath=config.settings.favorites_filepath
    ),
    "in_memory": InMemoryFavoritesService,
}

USER_IMPLEMENTATIONS: dict[str, Callable[..., interfaces.UserServiceInterface]] = {
    "postgres": PostgresUserService,
    "in_memory": InMemoryUserService,
}


# --- Service Dependency Providers ---
def get_favorites_service() -> interfaces.FavoritesServiceInterface:
    """Dependency provider for the favorites service."""
    factory = FAVORITES_IMPLEMENTATIONS.get(config.settings.favorites_implementation)
    if not factory:
        raise ValueError(
            f"Unknown favorites_implementation: '{config.settings.favorites_implementation}'"
        )
    return factory()


def get_user_service(db: DBSessionDep) -> interfaces.UserServiceInterface:
    """
    Dependency provider for the user service.
    Switches between Postgres and in-memory based on config.
    Crucially, it injects the database session into the Postgres service.
    """
    factory = USER_IMPLEMENTATIONS.get(config.settings.user_implementation)
    if not factory:
        raise ValueError(
            f"Unknown user_implementation: '{config.settings.user_implementation}'"
        )

    # If the chosen implementation is Postgres, it needs the 'db' session.
    if factory is PostgresUserService:
        return factory(db=db)
    # Otherwise, it's the in-memory service which doesn't need a db session.
    return factory()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(
    token: TokenDep,
    user_service: Annotated[interfaces.UserServiceInterface, Depends(get_user_service)],
) -> schemas.User:
    """
    Dependency to get the current authenticated user.
    It decodes the JWT token and returns the user model from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = user_service.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]
