"""API endpoints for user management."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_user_service
from ..interfaces import UserServiceInterface
from ..schemas import User, UserCreate

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

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, user_service: UserServiceDep):
    """Retrieve a user's public profile by their ID."""
    db_user = user_service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user