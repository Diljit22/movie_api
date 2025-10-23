"""
Main application file for the Movie API.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from movie_service.src.movie_api.routers import movies
from movie_service.src.movie_api.schemas import ErrorDetail, ErrorResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Prevents API leak in errors
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


# Global cache statistics
class CacheStats:
    """Thread-safe cache statistics tracker."""

    def __init__(self):
        self.l1_hits = 0
        self.l1_misses = 0
        self.l2_hits = 0
        self.l2_misses = 0
        self.api_calls = 0

    def record_l1_hit(self):
        self.l1_hits += 1

    def record_l1_miss(self):
        self.l1_misses += 1

    def record_l2_hit(self):
        self.l2_hits += 1

    def record_l2_miss(self):
        self.l2_misses += 1

    def record_api_call(self):
        self.api_calls += 1

    @property
    def total_requests(self):
        return self.l1_hits + self.l1_misses

    @property
    def l1_hit_rate(self):
        total = self.total_requests
        return (self.l1_hits / total * 100) if total > 0 else 0

    @property
    def l2_hit_rate(self):
        total = self.l2_hits + self.l2_misses
        return (self.l2_hits / total * 100) if total > 0 else 0

    def to_dict(self):
        return {
            "l1": {
                "hits": self.l1_hits,
                "misses": self.l1_misses,
                "hit_rate": f"{self.l1_hit_rate:.2f}%",
            },
            "l2": {
                "hits": self.l2_hits,
                "misses": self.l2_misses,
                "hit_rate": f"{self.l2_hit_rate:.2f}%",
            },
            "api_calls": self.api_calls,
            "total_requests": self.total_requests,
        }


cache_stats = CacheStats()


# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds a unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


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
