from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from user_service.src.user_api.config import settings
from user_service.src.user_api.dependencies import CurrentUserDep, get_favorites_service
from user_service.src.user_api.interfaces import FavoritesServiceInterface
from user_service.src.user_api.schemas import (
    AllFavoritesResponse,
    FavoriteResponse,
    IsFavoriteResponse,
)

router = APIRouter(prefix="/api/favorites", tags=["Favorites"])

FavoritesDep = Annotated[FavoritesServiceInterface, Depends(get_favorites_service)]


@router.get("/", response_model=AllFavoritesResponse)
async def get_favorites(current_user: CurrentUserDep, favorites_service: FavoritesDep):
    """
    Return all of the authenticated user's favorited movies with full details.
    This is achieved by calling the movie_service.
    """
    favorite_ids = favorites_service.get_all_for_user(user_id=current_user.id)

    if not favorite_ids:
        return {"favorites": []}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.movie_service_url}/api/movies/batch",
                json={"movie_ids": favorite_ids},
                timeout=5.0,
            )
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            movie_data = response.json()
            return {"favorites": movie_data.get("movies", [])}
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error communicating with movie service: {exc}",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error response from movie service: {exc.response.text}",
        ) from exc


@router.post(
    "/{movie_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED
)
def add_favorite(
    movie_id: int, current_user: CurrentUserDep, favorites_service: FavoritesDep
):
    """Add a movie to the authenticated user's favorites list."""
    favorites_service.add(user_id=current_user.id, movie_id=movie_id)
    return {
        "message": "Movie added to favorites",
        "user_id": current_user.id,
        "movie_id": movie_id,
    }


@router.delete("/{movie_id}", response_model=FavoriteResponse)
def remove_favorite(
    movie_id: int, current_user: CurrentUserDep, favorites_service: FavoritesDep
):
    """Remove a movie from the authenticated user's favorites list."""
    favorites_service.remove(user_id=current_user.id, movie_id=movie_id)
    return {
        "message": "Movie removed from favorites",
        "user_id": current_user.id,
        "movie_id": movie_id,
    }


@router.get("/{movie_id}/is-favorite", response_model=IsFavoriteResponse)
def check_favorite(
    movie_id: int, current_user: CurrentUserDep, favorites_service: FavoritesDep
):
    """Check if a movie is in the authenticated user's favorites."""
    is_fav = favorites_service.is_favorite(user_id=current_user.id, movie_id=movie_id)
    return {"is_favorite": is_fav}
