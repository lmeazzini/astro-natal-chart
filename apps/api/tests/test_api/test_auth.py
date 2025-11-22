"""
Tests for authentication endpoints and token refresh functionality.

Tests cover:
- Token verification endpoint
- Token refresh middleware
- Auto-refresh header detection
"""

from datetime import timedelta

from httpx import AsyncClient

from app.core.security import create_access_token, create_refresh_token
from app.models.user import User


class TestTokenVerify:
    """Tests for GET /api/v1/auth/verify endpoint."""

    async def test_verify_valid_token(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict[str, str],
    ):
        """Test verifying a valid token returns user info and expiration."""
        response = await client.get("/api/v1/auth/verify", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["valid"] is True
        assert data["user_id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert "expires_in" in data
        assert data["expires_in"] > 0  # Token should not be expired

    async def test_verify_expired_token(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that expired token returns 401."""
        # Create an already expired token
        expired_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-10),  # Already expired
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = await client.get("/api/v1/auth/verify", headers=headers)

        assert response.status_code == 401

    async def test_verify_invalid_token(self, client: AsyncClient):
        """Test that invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = await client.get("/api/v1/auth/verify", headers=headers)

        assert response.status_code == 401

    async def test_verify_no_token(self, client: AsyncClient):
        """Test that missing token returns 403 (forbidden)."""
        response = await client.get("/api/v1/auth/verify")

        # FastAPI returns 403 for missing credentials (401 requires WWW-Authenticate header)
        assert response.status_code == 403

    async def test_verify_returns_correct_expiration(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that expires_in reflects actual token expiration."""
        # Create token with known expiration
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(minutes=5),
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/auth/verify", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Should be approximately 5 minutes (300 seconds), allow 10 second margin
        assert 290 <= data["expires_in"] <= 310


class TestTokenRefreshMiddleware:
    """Tests for TokenRefreshMiddleware auto-refresh functionality."""

    async def test_normal_token_no_refresh_header(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that normal (not expiring soon) token doesn't trigger refresh."""
        # Create token with plenty of time remaining (10 minutes)
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(minutes=10),
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        # Should NOT have the refresh header
        assert "X-New-Access-Token" not in response.headers

    async def test_expiring_soon_token_gets_refresh_header(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that token expiring within 5 minutes triggers auto-refresh."""
        # Create token expiring in 2 minutes (within 5 minute threshold)
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(minutes=2),
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        # Should have the refresh header
        assert "X-New-Access-Token" in response.headers

        # New token should be valid
        new_token = response.headers["X-New-Access-Token"]
        assert len(new_token) > 0

        # Verify new token works
        new_headers = {"Authorization": f"Bearer {new_token}"}
        verify_response = await client.get("/api/v1/auth/me", headers=new_headers)
        assert verify_response.status_code == 200

    async def test_refresh_header_exposed_in_cors(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that X-New-Access-Token is in Access-Control-Expose-Headers."""
        # Create token expiring soon
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(minutes=2),
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        expose_headers = response.headers.get("Access-Control-Expose-Headers", "")
        assert "X-New-Access-Token" in expose_headers

    async def test_invalid_token_no_crash(self, client: AsyncClient):
        """Test that invalid token doesn't crash middleware."""
        headers = {"Authorization": "Bearer malformed.token.here"}

        response = await client.get("/api/v1/auth/me", headers=headers)

        # Should return 401 without crashing
        assert response.status_code == 401

    async def test_no_auth_header_passes_through(self, client: AsyncClient):
        """Test that requests without auth header pass through middleware."""
        response = await client.get("/health")

        assert response.status_code == 200
        assert "X-New-Access-Token" not in response.headers


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    async def test_refresh_with_valid_refresh_token(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test refreshing access token with valid refresh token."""
        refresh_token = create_refresh_token(data={"sub": str(test_user.id)})

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify new access token works
        new_headers = {"Authorization": f"Bearer {data['access_token']}"}
        verify_response = await client.get("/api/v1/auth/me", headers=new_headers)
        assert verify_response.status_code == 200

    async def test_refresh_with_invalid_refresh_token(
        self,
        client: AsyncClient,
    ):
        """Test that invalid refresh token returns 401."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "completely_invalid_token"},
        )

        assert response.status_code == 401

    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test that invalid refresh token returns 401."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401

    async def test_refresh_with_access_token_type(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that using access token (wrong type) for refresh fails."""
        # Access token has no "type": "refresh" claim
        access_token = create_access_token(data={"sub": str(test_user.id)})

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401
        # The endpoint returns generic "Invalid refresh token" for security
        assert "Invalid" in response.json()["detail"]

    async def test_refresh_with_nonexistent_user(
        self,
        client: AsyncClient,
    ):
        """Test refresh with token for deleted user fails."""
        from uuid import uuid4

        # Create refresh token for non-existent user
        fake_user_id = str(uuid4())
        refresh_token = create_refresh_token(data={"sub": fake_user_id})

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401


class TestLoginTokens:
    """Tests for login endpoint token generation."""

    async def test_login_returns_both_tokens(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that login returns both access and refresh tokens."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Both tokens should be non-empty
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    async def test_access_token_short_lived(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test that access token has short expiration (15 min default)."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#",
            },
        )

        assert response.status_code == 200
        access_token = response.json()["access_token"]

        # Verify token expiration via verify endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        verify_response = await client.get("/api/v1/auth/verify", headers=headers)

        assert verify_response.status_code == 200
        # Default is 15 minutes = 900 seconds
        assert verify_response.json()["expires_in"] <= 900
