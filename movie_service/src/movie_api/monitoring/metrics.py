"""
Prometheus metrics for monitoring application performance.
"""

from prometheus_client import Counter, Histogram

# HTTP Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_RESPONSE_TIME_SECONDS = Histogram(
    "http_response_time_seconds", "HTTP request duration in seconds", ["method", "path"]
)

# Cache Metrics
CACHE_HITS_TOTAL = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_level"],  # "l1" or "l2"
)

CACHE_MISSES_TOTAL = Counter(
    "cache_misses_total", "Total number of cache misses", ["cache_level"]
)

TMDB_API_CALLS_TOTAL = Counter(
    "tmdb_api_calls_total",
    "Total number of calls to TMDB API",
    ["endpoint"],  # e.g., "get_movie_details", "get_trending_movies", "search_movies"
)
