"""
Defines the data structures for API responses and error models.

These schemas are used by FastAPI for data validation, serialization,
and generating OpenAPI documentation.
"""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Defines the structure for a detailed error message."""

    message: str


class ErrorResponse(BaseModel):
    """Defines the standardized JSON structure for API error responses."""

    detail: ErrorDetail


class MovieBase(BaseModel):
    """Base model for a movie, containing common fields."""

    id: int
    title: str
    overview: str
    poster_path: str | None = None
    release_date: str


class TrendingMoviesResponse(BaseModel):
    """Defines the response structure for the trending movies endpoint."""

    page: int
    results: list[MovieBase]
    total_pages: int
    total_results: int


class MovieDetail(MovieBase):
    """Extends the base movie model with additional details."""

    tagline: str | None = None
    status: str
    vote_average: float
    vote_count: int
