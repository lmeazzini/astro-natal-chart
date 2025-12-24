"""
View deduplication service using Redis.

Prevents view count gaming by tracking recent views per IP/slug combination.
Only allows one view count increment per IP per chart within a time window.
"""

import hashlib

import redis
from loguru import logger

from app.core.config import settings

# View deduplication window in seconds (30 minutes)
VIEW_DEDUP_WINDOW_SECONDS = 30 * 60

# Redis key prefix for view deduplication
VIEW_DEDUP_KEY_PREFIX = "view_dedup:"


def _get_redis_client() -> redis.Redis | None:
    """
    Get a Redis client connection.

    Returns:
        Redis client or None if connection fails
    """
    try:
        return redis.from_url(str(settings.REDIS_URL), decode_responses=True)
    except Exception as e:
        logger.warning(f"Failed to connect to Redis for view deduplication: {e}")
        return None


def _generate_view_key(slug: str, client_ip: str) -> str:
    """
    Generate a unique Redis key for view tracking.

    Uses a hash of the IP to reduce key size and avoid storing raw IPs.

    Args:
        slug: Chart slug
        client_ip: Client IP address

    Returns:
        Redis key string
    """
    # Hash the IP for privacy and to reduce key size
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    return f"{VIEW_DEDUP_KEY_PREFIX}{slug}:{ip_hash}"


def should_increment_view(slug: str, client_ip: str) -> bool:
    """
    Check if view should be incremented (no recent view from this IP).

    Args:
        slug: Chart slug
        client_ip: Client IP address

    Returns:
        True if view should be counted, False if already viewed recently
    """
    client = _get_redis_client()
    if not client:
        # If Redis is unavailable, allow the increment (fail open)
        logger.debug("Redis unavailable, allowing view increment")
        return True

    try:
        key = _generate_view_key(slug, client_ip)

        # Check if key exists
        if client.exists(key):
            logger.debug(f"View dedup: already viewed recently ({slug})")
            return False

        # Set key with expiration
        client.setex(key, VIEW_DEDUP_WINDOW_SECONDS, "1")
        logger.debug(f"View dedup: new view recorded ({slug})")
        return True

    except Exception as e:
        logger.warning(f"Redis error in view deduplication: {e}")
        # On error, allow the increment (fail open)
        return True
    finally:
        client.close()
