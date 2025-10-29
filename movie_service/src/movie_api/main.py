"""
Main application file for the Movie API.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import make_asgi_app

from movie_service.src.movie_api.dependencies import (
    get_distributed_cache,
    get_in_memory_cache,
    get_movie_service,
)
from movie_service.src.movie_api.middleware.request_id import RequestIDMiddleware
from movie_service.src.movie_api.monitoring import metrics
from movie_service.src.movie_api.monitoring.cache_stats import cache_stats
from movie_service.src.movie_api.routers import movies
from movie_service.src.movie_api.schemas import ErrorDetail, ErrorResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Prevents API leak in errors
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def warm_cache():
    """A background task to periodically refresh the trending movies cache."""
    l1_cache = get_in_memory_cache()
    l2_cache = get_distributed_cache()
    movie_service = get_movie_service()

    while True:
        try:
            logging.info("Cache warming: Fetching daily trending movies...")
            trending_movies = await movie_service.get_trending_movies(time_window="day")
            cache_key = "trending_movies_day"

            # Populate both caches
            await l2_cache.set(cache_key, trending_movies)
            await l1_cache.set(cache_key, trending_movies)

            logging.info("Cache warming: Daily trending movies cache refreshed.")
        except Exception as e:
            logging.error(f"Cache warming task failed: {e}")

        # Wait for 10 minutes (600 seconds) before the next run
        await asyncio.sleep(600)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    # Startup
    logging.info("Movie API starting up...")

    asyncio.create_task(warm_cache())
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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add a process time header and record Prometheus metrics."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)

    # Record Prometheus metrics
    path = request.url.path
    metrics.HTTP_RESPONSE_TIME_SECONDS.labels(method=request.method, path=path).observe(
        process_time
    )

    metrics.HTTP_REQUESTS_TOTAL.labels(
        method=request.method, path=path, status_code=response.status_code
    ).inc()

    return response


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
    return {
        "status": "ok",
        "message": "Movie API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "movie-service",
        "version": "1.0.0",
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
    cache_stats.reset()
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
