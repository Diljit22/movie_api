"""Middleware components for request processing."""

from movie_service.src.movie_api.middleware.request_id import RequestIDMiddleware

__all__ = ["RequestIDMiddleware"]
