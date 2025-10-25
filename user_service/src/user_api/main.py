"""
Main application file for the User API.

Initializes the FastAPI application, sets up middleware, routers,
and exception handlers.
"""
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from . import database, models
from .middleware.request_id import RequestIDMiddleware
from .routers import favorites, users
from .schemas import ErrorDetail, ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    logging.info("User API starting up...")
    logging.info("Creating database tables...")
    # This command creates all tables defined in models.py that don't already exist
    database.Base.metadata.create_all(bind=database.engine)
    logging.info("Database tables created.")
    yield
    logging.info("User API shutting down...")

app = FastAPI(
    title="User API", version="1.0.0",
    description="API for managing users and their favorite movies.",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
        content=ErrorResponse(detail=ErrorDetail(message=exc.detail)).model_dump())

app.include_router(users.router)
app.include_router(favorites.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to the User API!"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat(), "service": "user-service"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)