"""
Test configuration and fixtures.

This module provides pytest fixtures and configuration for the test suite.
"""

import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from redis import asyncio as aioredis

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def reset_rate_limits():
    """Reset rate limits before each test by clearing Redis."""
    # Connect to Redis
    redis = await aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)

    try:
        # Clear all rate limit keys (they start with "LIMITER")
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="LIMITER*", count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break

        yield

    finally:
        await redis.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
