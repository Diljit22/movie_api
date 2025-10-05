"""
Main application file for the Movie API.
"""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response

from movie_api.routers import favorites, movies
from movie_api.schemas import ErrorDetail, ErrorResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Prevents API leak in errors
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# FastAPI app instance
app = FastAPI(
    title="Movie API",
    version="1.0.0",
    description="Movie API with TMDB integration",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Exception handler ensuring all API errors return a standardized JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=ErrorDetail(message=exc.detail)).model_dump(),
    )


app.include_router(movies.router)
app.include_router(favorites.router)


@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm that the API is running."""
    return {"status": "ok", "message": "Movie API is running."}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    An endpoint to handle the browser's automatic request for a favicon.
    It returns a 204 No Content response to prevent 404 errors in the logs.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
