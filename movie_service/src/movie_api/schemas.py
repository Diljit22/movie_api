"""
Defines the data structures for API responses and error models.

These schemas are used by FastAPI for data validation, serialization,
and generating OpenAPI documentation.
"""

from pydantic import BaseModel, Field


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


class BatchMovieRequest(BaseModel):
    """Request model for batch movie fetching."""

    movie_ids: list[int] = Field(
        ...,
        description="List of movie IDs to fetch",
        min_length=1,
        max_length=50,
        examples=[[550, 551, 552]],
    )


class BatchMovieError(BaseModel):
    """Error details for a failed movie fetch in batch operation."""

    movie_id: int
    error: str


class BatchMovieResponse(BaseModel):
    """Response model for batch movie fetching."""

    movies: list[MovieDetail] = Field(
        ..., description="Successfully fetched movie details"
    )
    total_requested: int = Field(
        ..., description="Total number of unique movies requested"
    )
    total_found: int = Field(..., description="Number of movies successfully fetched")
    errors: list[BatchMovieError] | None = Field(
        None, description="List of movies that failed to fetch"
    )
