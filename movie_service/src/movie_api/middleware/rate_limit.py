"""
Rate limiting middleware using slowapi.

Protects API endpoints from abuse by limiting requests per time window.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
# Uses remote IP address as the key for rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
