"""
Dependency Injection providers.

Contains functions that FastAPI's `Depends` system will use to
create and inject instances of our service and cache classes into the
API route handlers.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from . import config, interfaces
from .database import SessionLocal
from .services.favorites_service_json import JSONFileFavoritesService
from .services.in_memory_favorites import InMemoryFavoritesService
from .services.in_memory_users import InMemoryUserService
from .services.user_service_postgres import PostgresUserService


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
FAVORITES_IMPLEMENTATIONS = {
    "json_file": lambda: JSONFileFavoritesService(filepath=config.settings.favorites_filepath),
    "in_memory": InMemoryFavoritesService,
}

USER_IMPLEMENTATIONS = {
    "postgres": PostgresUserService,
    "in_memory": InMemoryUserService,
}


# --- Service Dependency Providers ---
def get_favorites_service() -> interfaces.FavoritesServiceInterface:
    """Dependency provider for the favorites service."""
    factory = FAVORITES_IMPLEMENTATIONS.get(config.settings.favorites_implementation)
    if not factory:
        raise ValueError(f"Unknown favorites_implementation: '{config.settings.favorites_implementation}'")
    return factory()


def get_user_service(db: DBSessionDep) -> interfaces.UserServiceInterface:
    """
    Dependency provider for the user service.
    Switches between Postgres and in-memory based on config.
    Crucially, it injects the database session into the Postgres service.
    """
    factory = USER_IMPLEMENTATIONS.get(config.settings.user_implementation)
    if not factory:
        raise ValueError(f"Unknown user_implementation: '{config.settings.user_implementation}'")
    
    # If the chosen implementation is Postgres, it needs the 'db' session.
    if factory is PostgresUserService:
        return factory(db=db)
    # Otherwise, it's the in-memory service which doesn't need a db session.
    return factory()