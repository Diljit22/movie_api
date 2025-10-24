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
