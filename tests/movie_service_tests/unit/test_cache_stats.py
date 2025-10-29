from movie_service.src.movie_api.monitoring.cache_stats import CacheStats


def test_cache_stats_initialization():
    """Tests that CacheStats initializes with all counters at zero."""
    stats = CacheStats()
    assert stats.l1_hits == 0 and stats.l1_misses == 0
    assert stats.l2_hits == 0 and stats.l2_misses == 0
    assert stats.api_calls == 0 and stats.total_requests == 0


def test_cache_stats_recording():
    """Tests the recording methods increment the correct counters."""
    stats = CacheStats()
    stats.record_l1_hit()
    stats.record_l1_miss()
    stats.record_l1_miss()
    stats.record_l2_hit()
    stats.record_l2_miss()
    stats.record_api_call()
    assert stats.l1_hits == 1 and stats.l1_misses == 2
    assert stats.l2_hits == 1 and stats.l2_misses == 1
    assert stats.api_calls == 1 and stats.total_requests == 3


def test_cache_stats_hit_rate_calculation():
    """Tests the hit rate calculation properties."""
    stats = CacheStats()
    stats.record_l1_hit()  # 1 hit, 3 misses -> 25% L1 hit rate
    stats.record_l1_miss()
    stats.record_l1_miss()
    stats.record_l1_miss()
    stats.record_l2_hit()
    stats.record_l2_hit()  # 2 hits, 1 miss -> 66.67% L2
    stats.record_l2_miss()
    assert stats.l1_hit_rate == 25.0
    assert abs(stats.l2_hit_rate - 66.67) < 0.01


def test_cache_stats_hit_rate_division_by_zero():
    """Tests that hit rate is 0 when there are no requests."""
    stats = CacheStats()
    assert stats.l1_hit_rate == 0 and stats.l2_hit_rate == 0


def test_cache_stats_to_dict():
    """Tests the dictionary representation of the stats."""
    stats = CacheStats()
    stats.record_l1_hit()
    stats.record_l1_miss()
    data = stats.to_dict()
    assert data["l1"]["hits"] == 1 and data["l1"]["misses"] == 1
    assert data["l1"]["hit_rate"] == "50.00%"


def test_cache_stats_reset():
    """Tests that the reset method sets all counters back to zero."""
    stats = CacheStats()
    stats.record_api_call()
    stats.record_l1_hit()
    stats.reset()
    assert stats.api_calls == 0 and stats.l1_hits == 0
