"""
Main application file for the Movie API.
"""

from fastapi import FastAPI, status
from fastapi.responses import Response

# TODO Add logging


# FastAPI app instance
app = FastAPI(
    title="Movie API",
    version="1.0.0",
    description="Movie API with TMDB integration",
)


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
