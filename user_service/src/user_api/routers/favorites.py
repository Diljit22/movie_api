from typing import Annotated
from fastapi import APIRouter, Depends, status
from user_service.src.user_api.dependencies import get_favorites_service
from user_service.src.user_api.interfaces import FavoritesServiceInterface
from user_service.src.user_api.schemas import (
    AllFavoritesResponse, FavoriteResponse, IsFavoriteResponse
)

router = APIRouter(prefix="/api/users/{user_id}/favorites", tags=["Favorites"])

FavoritesDep = Annotated[FavoritesServiceInterface, Depends(get_favorites_service)]

@router.get("/", response_model=AllFavoritesResponse)
def get_favorites(user_id: int, favorites_service: FavoritesDep):
    """Return all favorited movie IDs for a specific user."""
    return {"favorites": favorites_service.get_all_for_user(user_id=user_id)}

@router.post(
    "/{movie_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED
)
def add_favorite(user_id: int, movie_id: int, favorites_service: FavoritesDep):
    """Add a movie to the user's favorites list."""
    favorites_service.add(user_id=user_id, movie_id=movie_id)
    return {
        "message": "Movie added to favorites",
        "user_id": user_id,
        "movie_id": movie_id,
    }

@router.delete("/{movie_id}", response_model=FavoriteResponse)
def remove_favorite(user_id: int, movie_id: int, favorites_service: FavoritesDep):
    """Remove a movie from the user's favorites list."""
    favorites_service.remove(user_id=user_id, movie_id=movie_id)
    return {
        "message": "Movie removed from favorites",
        "user_id": user_id,
        "movie_id": movie_id,
    }

@router.get("/{movie_id}/is-favorite", response_model=IsFavoriteResponse)
def check_favorite(user_id: int, movie_id: int, favorites_service: FavoritesDep):
    """Check if a movie is in the user's favorites."""
    is_fav = favorites_service.is_favorite(user_id=user_id, movie_id=movie_id)
    return {"is_favorite": is_fav}