"""API endpoints for user management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from user_service.src.user_api.dependencies import CurrentUserDep, get_user_service
from user_service.src.user_api.interfaces import UserServiceInterface
from user_service.src.user_api.schemas import User, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])

UserServiceDep = Annotated[UserServiceInterface, Depends(get_user_service)]


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, user_service: UserServiceDep):
    """
    Register a new user.

    - **username**: Must be between 3 and 50 characters.
    - **email**: Must be a valid email format.
    - **password**: Must be at least 8 characters long.
    """
    db_user = user_service.get_user_by_email(email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return user_service.create_user(user_data=user_data)


@router.get("/me", response_model=User)
def read_users_me(current_user: CurrentUserDep):
    """Get the profile of the currently authenticated user."""
    return current_user


@router.put("/me", response_model=User)
def update_users_me(
    user_data: UserUpdate, current_user: CurrentUserDep, user_service: UserServiceDep
):
    """Update the profile of the currently authenticated user."""
    updated_user = user_service.update_user(
        user_id=current_user.id, user_data=user_data
    )
    if updated_user is None:
        # This case should ideally not happen if the user is authenticated
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/me", response_model=User)
def delete_users_me(current_user: CurrentUserDep, user_service: UserServiceDep):
    """Delete the profile of the currently authenticated user."""
    deleted_user = user_service.delete_user(user_id=current_user.id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, user_service: UserServiceDep):
    """Retrieve a user's public profile by their ID."""
    db_user = user_service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user
