"""
Rate limiting configuration using SlowAPI.

This module provides rate limiting functionality for FastAPI endpoints
using Redis as the storage backend.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def get_real_client_ip(request: Request) -> str:
    """
    Extract real client IP from request, handling reverse proxy headers.

    Checks X-Forwarded-For and X-Real-IP headers before falling back
    to the direct connection address.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check X-Forwarded-For header (set by reverse proxies like Nginx)
    # Format: "client, proxy1, proxy2" - first IP is the real client
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded_for:
        return forwarded_for

    # Check X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("X-Real-IP", "").strip()
    if real_ip:
        return real_ip

    # Fallback to direct connection address
    return get_remote_address(request)


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
    if hasattr(request.state, "user") and request.state.user:
        user_id = getattr(request.state.user, "id", None)
        if user_id:
            return f"user:{user_id}"

    # Fallback to real client IP for public endpoints
    return f"ip:{get_real_client_ip(request)}"


# Initialize rate limiter with Redis storage
limiter = Limiter(
    key_func=get_identifier_from_request,
    storage_uri=str(settings.REDIS_URL),
    default_limits=[],  # No default limits, set per-endpoint
    headers_enabled=True,  # Include X-RateLimit-* headers in responses
    enabled=settings.RATE_LIMIT_ENABLED,  # Can be disabled for testing
)


# Pre-configured limit strings for common use cases
class RateLimits:
    """Centralized rate limit configurations."""

    # Authentication endpoints (by IP)
    LOGIN = "10/minute"  # 10 login attempts per minute
    REGISTER = "20/hour"  # 20 registrations per hour per IP
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

    # Password Reset endpoints (by IP)
    PASSWORD_RESET_REQUEST = "3/hour"  # 3 reset requests per hour
    PASSWORD_RESET_CONFIRM = "5/hour"  # 5 reset confirmations per hour

    # Admin endpoints (by user_id - admin only)
    ADMIN_ROLE_UPDATE = "10/hour"  # 10 role updates per hour

    # Avatar Upload (by user_id - heavier operation)
    AVATAR_UPLOAD = "10/hour"  # 10 avatar uploads per hour

    # RAG endpoints (by user_id - resource intensive)
    RAG_SEARCH = "30/minute"  # 30 searches per minute
    RAG_INGEST_TEXT = "20/hour"  # 20 text ingestions per hour
    RAG_INGEST_PDF = "10/hour"  # 10 PDF ingestions per hour (heavy operation)
    RAG_DELETE = "30/hour"  # 30 document deletions per hour
    RAG_STATS = "60/minute"  # 60 stats requests per minute

    # Cache management endpoints (by user_id - admin only)
    CACHE_STATS = "60/minute"  # 60 stats requests per minute
    CACHE_CLEAR = "10/hour"  # 10 clear operations per hour (destructive)

    # Personal growth suggestions (by user_id - expensive AI operations)
    GROWTH_SUGGESTIONS = "10/hour"  # 10 growth suggestions per hour
