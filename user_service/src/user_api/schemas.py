"""
Defines data structures for API requests, responses, and error models.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ErrorDetail(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["john_doe"])
    email: EmailStr = Field(..., examples=["johndoe@example.com"])


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, examples=["a-very-strong-password123!"])


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response model for the /login endpoint."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for the data encoded within the JWT."""

    sub: str | None = None


class Movie(BaseModel):
    id: int
    title: str
    overview: str
    poster_path: str | None = None
    release_date: str


class FavoriteResponse(BaseModel):
    message: str
    user_id: int
    movie_id: int


class IsFavoriteResponse(BaseModel):
    is_favorite: bool


class AllFavoritesResponse(BaseModel):
    favorites: list[Movie]


class UserUpdate(BaseModel):
    """Schema for updating a user's profile. All fields are optional."""

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
