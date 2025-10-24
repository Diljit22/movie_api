from prometheus_client import Counter, Gauge, Histogram

# Metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

cache_hit_rate = Gauge("cache_hit_rate", "Cache hit rate percentage", ["cache_level"])

response_time = Histogram(
    "http_response_time_seconds", "HTTP response time", ["method", "endpoint"]
)
