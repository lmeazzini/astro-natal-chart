"""
Tests for rate limiting functionality.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient):
    """Test rate limiting on login endpoint (10 requests per minute)."""
    # First 10 requests should succeed (401 for invalid credentials, but not rate limited)
    for i in range(10):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": f"test{i}@example.com", "password": "wrongpassword"},
        )
        # Should get 401 Unauthorized, not 429 (rate limit exceeded)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    # 11th request should be rate limited
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # Check rate limit headers are present
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "Retry-After" in response.headers


@pytest.mark.asyncio
async def test_register_rate_limit(client: AsyncClient):
    """Test rate limiting on register endpoint (5 requests per hour)."""
    # First 5 requests
    for i in range(5):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"newuser{i}@example.com",
                "password": "ValidPassword123!",
                "password_confirm": "ValidPassword123!",
                "full_name": f"Test User {i}",
                "accept_terms": True,
            },
        )
        # Should process (might succeed or fail due to DB, but not rate limited)
        assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    # 6th request should be rate limited
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser6@example.com",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
            "full_name": "Test User 6",
            "accept_terms": True,
        },
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_geocoding_rate_limit(client: AsyncClient):
    """Test rate limiting on geocoding search endpoint (60 requests per minute)."""
    import respx
    from httpx import Response

    # Mock Nominatim API responses
    with respx.mock:
        respx.get("https://nominatim.openstreetmap.org/search").mock(
            return_value=Response(200, json=[])
        )

        # First 60 requests should succeed (return 200)
        for i in range(60):
            response = await client.get(
                "/api/v1/geocoding/search",
                params={"q": f"City{i}", "limit": 1},
            )
            # Should process (returns 200, but not rate limited)
            assert response.status_code == status.HTTP_200_OK

        # 61st request should be rate limited
        response = await client.get(
            "/api/v1/geocoding/search",
            params={"q": "TestCity", "limit": 1},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_rate_limit_headers(client: AsyncClient):
    """Test that rate limit response includes correct headers."""
    # Make enough requests to trigger rate limit
    for _ in range(10):  # Login limit is 10/minute
        await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

    # This one should be rate limited (11th request)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # Validate headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert int(response.headers["X-RateLimit-Remaining"]) == 0

    assert "Retry-After" in response.headers
    retry_after = int(response.headers["Retry-After"])
    assert 0 < retry_after <= 60  # Should be within 1 minute


@pytest.mark.skip(reason="Cannot properly test different IPs with AsyncClient")
@pytest.mark.asyncio
async def test_rate_limit_different_ips():
    """Test that rate limits are per-IP (different IPs get separate limits)."""
    # Note: This test is simplified and won't actually work in TestClient
    # because we can't easily spoof different IPs in HTTPX
    # In a real integration test with docker/kubernetes, you could test this properly
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make requests from "same IP" (test client default)
        for _ in range(10):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "user1@example.com", "password": "pass"},
            )
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

        # 11th should be rate limited
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "pass"},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.skip(reason="OAuth tests require SessionMiddleware configuration")
@pytest.mark.asyncio
async def test_oauth_rate_limit():
    """Test rate limiting on OAuth endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test OAuth login endpoint (10 requests per minute)
        for _i in range(10):
            response = await client.get(
                "/api/v1/oauth/login/google",
            )
            # OAuth might redirect or error, but shouldn't be rate limited yet
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

        # 11th request should be rate limited
        response = await client.get("/api/v1/oauth/login/google")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
