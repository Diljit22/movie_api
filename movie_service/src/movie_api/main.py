"""
Main application file for the Movie API.
"""

import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import make_asgi_app

from movie_service.src.movie_api.middleware.request_id import RequestIDMiddleware
from movie_service.src.movie_api.monitoring.cache_stats import CacheStats
from movie_service.src.movie_api.routers import movies
from movie_service.src.movie_api.schemas import ErrorDetail, ErrorResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Prevents API leak in errors
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    # Startup
    logging.info("Movie API starting up...")
    yield
    # Shutdown
    logging.info("Movie API shutting down...")


# FastAPI app instance
app = FastAPI(
    title="Movie API",
    version="1.0.0",
    description="Movie API with TMDB integration and multi-level caching",
)

metrics_app = make_asgi_app()
app.mount("/prometheus", metrics_app)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Exception handler ensuring all API errors return a standardized JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=ErrorDetail(message=exc.detail)).model_dump(),
    )


app.include_router(movies.router)


@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm that the API is running."""
    return {"status": "ok", "message": "Movie API is running."}


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "movie-service",
    }


@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """Returns cache performance metrics."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "cache_stats": cache_stats.to_dict(),
    }


@app.post("/metrics/reset", tags=["Metrics"])
async def reset_metrics():
    """Resets cache statistics (useful for testing)."""
    global cache_stats
    cache_stats = CacheStats()
    return {
        "status": "reset",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    An endpoint to handle the browser's automatic request for a favicon.
    It returns a 204 No Content response to prevent 404 errors in the logs.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
