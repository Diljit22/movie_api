"""
API endpoints for favorites.

This router is decoupled from the underlying service implementations
through the use of FastAPI's dependency injection system.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from movie_api.dependencies import get_favorites_service
from movie_api.interfaces import FavoritesInterface
from movie_api.schemas import AllFavoritesResponse, FavoriteResponse, IsFavoriteResponse

router = APIRouter(prefix="/api/favorites", tags=["Favorites"])

FavoritesInterDep = Annotated[FavoritesInterface, Depends(get_favorites_service)]


@router.get("/", response_model=AllFavoritesResponse)
async def get_favorites(favorites: FavoritesInterDep):
    """Return all favorited movie IDs."""
    return {"favorites": favorites.get_all()}


@router.post(
    "/{movie_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED
)
async def add_favorite(movie_id: int, favorites: FavoritesInterDep):
    """Add a movie to the favorites list (creates a new resource, status_code=201)."""
    favorites.add(movie_id)
    return {"message": "Movie added to favorites", "movie_id": movie_id}


@router.delete("/{movie_id}", response_model=FavoriteResponse)
async def remove_favorite(movie_id: int, favorites: FavoritesInterDep):
    """Remove a movie from the favorites list; status_code=200 used."""
    favorites.remove(movie_id)
    return {"message": "Movie removed from favorites", "movie_id": movie_id}


@router.get("/{movie_id}/is-favorite", response_model=IsFavoriteResponse)
async def check_favorite(movie_id: int, favorites: FavoritesInterDep):
    """Check whether a movie is currently marked as favorite."""
    return {"is_favorite": favorites.is_favorite(movie_id)}
