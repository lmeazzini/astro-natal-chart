"""
Rate limiting configuration using SlowAPI.

This module provides rate limiting functionality for FastAPI endpoints
using Redis as the storage backend.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def get_identifier_from_request(request: Request) -> str:
    """
    Get identifier for rate limiting from request.

    Strategy:
    - For authenticated endpoints: use user_id from JWT token
    - For public endpoints: use client IP address

    Args:
        request: FastAPI request object

    Returns:
        Identifier string (user_id or IP address)
    """
    # Try to get user from request state (set by get_current_user dependency)
    if hasattr(request.state, 'user') and request.state.user:
        user_id = getattr(request.state.user, 'id', None)
        if user_id:
            return f"user:{user_id}"

    # Fallback to IP address for public endpoints
    return f"ip:{get_remote_address(request)}"


# Initialize rate limiter with Redis storage
limiter = Limiter(
    key_func=get_identifier_from_request,
    storage_uri=str(settings.REDIS_URL),
    default_limits=[],  # No default limits, set per-endpoint
    headers_enabled=True,  # Include X-RateLimit-* headers in responses
)


# Pre-configured limit strings for common use cases
class RateLimits:
    """Centralized rate limit configurations."""

    # Authentication endpoints (by IP)
    LOGIN = "10/minute"  # 10 login attempts per minute
    REGISTER = "5/hour"  # 5 registrations per hour
    REFRESH = "10/minute"  # 10 token refreshes per minute

    # Chart endpoints (by user_id)
    CHART_CREATE = "30/hour"  # 30 chart creations per hour
    CHART_LIST = "100/minute"  # 100 list requests per minute
    CHART_READ = "200/minute"  # 200 individual chart reads per minute
    CHART_UPDATE = "60/hour"  # 60 updates per hour
    CHART_DELETE = "30/hour"  # 30 deletions per hour

    # Geocoding endpoints (by IP - external API calls)
    GEOCODING_SEARCH = "60/minute"  # 60 searches per minute
    GEOCODING_COORDINATES = "60/minute"  # 60 coordinate lookups per minute

    # OAuth endpoints (by IP)
    OAUTH_LOGIN = "10/minute"  # 10 OAuth initiations per minute
    OAUTH_CALLBACK = "10/minute"  # 10 OAuth callbacks per minute
