"""
Defines data structures for API requests, responses, and error models.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ErrorDetail(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: ErrorDetail


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic v2 alias for orm_mode


class FavoriteResponse(BaseModel):
    message: str
    user_id: int
    movie_id: int

class IsFavoriteResponse(BaseModel):
    is_favorite: bool

class AllFavoritesResponse(BaseModel):
    favorites: list[int]