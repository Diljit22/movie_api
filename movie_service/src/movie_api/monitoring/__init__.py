"""Monitoring and metrics collection."""

from movie_service.src.movie_api.monitoring import metrics
from movie_service.src.movie_api.monitoring.cache_stats import CacheStats, cache_stats

__all__ = ["cache_stats", "CacheStats", "metrics"]
