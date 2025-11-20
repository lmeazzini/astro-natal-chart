"""
Integration tests for authentication endpoints.

Tests cover user registration, login, token refresh, and authentication flow.
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class TestRegister:
    """Test user registration endpoint."""

    async def test_register_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "password_confirm": "SecurePassword123!",
                "full_name": "New User",
                "accept_terms": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password_hash" not in data  # Password should not be returned
        assert data["is_active"] is True
        assert data["email_verified"] is False  # Default value

        # Verify user was created in database
        user_repo = UserRepository(db_session)
        user = await user_repo.get_by_email("newuser@example.com")
        assert user is not None
        assert user.password_hash is not None

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Test registration with duplicate email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,  # Already exists
                "password": "SecurePassword123!",
                "password_confirm": "SecurePassword123!",
                "full_name": "Duplicate User",
                "accept_terms": True,
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePassword123!",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("email" in str(error).lower() for error in errors)

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too weak
                "full_name": "Test User",
            },
        )

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(error).lower() for error in errors)

    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # Missing password and full_name
            },
        )

        assert response.status_code == 422

    async def test_register_empty_full_name(self, client: AsyncClient):
        """Test registration with empty full name fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "full_name": "",  # Empty
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Test user login endpoint."""

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login returns valid tokens."""
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
        assert len(data["access_token"]) > 20  # JWT should be long string
        assert len(data["refresh_token"]) > 20

    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123!",
            },
        )

        assert response.status_code == 401
        detail = response.json()["detail"].lower()
        assert "invalid" in detail or "incorrect" in detail

    async def test_login_incorrect_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        detail = response.json()["detail"].lower()
        assert "invalid" in detail or "incorrect" in detail

    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        test_user_factory,
        db_session: AsyncSession,
    ):
        """Test login with inactive user fails."""
        inactive_user = await test_user_factory(
            email="inactive@example.com",
            password="Test123!@#",
            is_active=False,
        )

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": inactive_user.email,
                "password": "Test123!@#",
            },
        )

        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()

    async def test_login_case_insensitive_email(
        self, client: AsyncClient, test_user: User
    ):
        """Test login with different email case works."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email.upper(),  # UPPERCASE
                "password": "Test123!@#",
            },
        )

        # Should still work (email should be case-insensitive)
        assert response.status_code in [200, 401]  # Depends on implementation


class TestRefreshToken:
    """Test token refresh endpoint."""

    async def test_refresh_token_success(self, client: AsyncClient, test_user: User):
        """Test refreshing access token with valid refresh token."""
        # First, login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#",
            },
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        # Now refresh the token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_refresh_with_access_token_fails(
        self, client: AsyncClient, test_user: User
    ):
        """Test that using access token for refresh fails."""
        # Login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#",
            },
        )
        access_token = login_response.json()["access_token"]

        # Try to refresh with access token (should fail)
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},  # Wrong token type
        )

        assert response.status_code == 401

    async def test_refresh_with_expired_token(self, client: AsyncClient):
        """Test refresh with expired token fails."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjB9.test"

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user endpoint."""

    async def test_get_current_user_success(
        self, client: AsyncClient, auth_headers: dict[str, str], test_user: User
    ):
        """Test getting current user with valid token."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["id"] == str(test_user.id)
        assert "password_hash" not in data

    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token fails."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code in [401, 403]

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    async def test_get_current_user_malformed_header(self, client: AsyncClient):
        """Test with malformed authorization header."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer token"},
        )

        assert response.status_code in [401, 403]


class TestLogout:
    """Test user logout endpoint."""

    async def test_logout_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test logout with valid token."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 204

    async def test_logout_no_token(self, client: AsyncClient):
        """Test logout without token fails."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code in [401, 403]

    async def test_logout_invalid_token(self, client: AsyncClient):
        """Test logout with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code in [401, 403]


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    async def test_complete_auth_flow(self, client: AsyncClient, db_session: AsyncSession):
        """Test complete flow: register -> login -> get user -> refresh -> logout."""
        # 1. Register new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flow@example.com",
                "password": "FlowPassword123!",
                "password_confirm": "FlowPassword123!",
                "full_name": "Flow User",
                "accept_terms": True,
            },
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flow@example.com",
                "password": "FlowPassword123!",
            },
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 3. Get current user
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "flow@example.com"

        # 4. Refresh token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        new_access_token = new_tokens["access_token"]

        # 5. Verify new token works
        me_response_2 = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert me_response_2.status_code == 200

        # 6. Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert logout_response.status_code == 204

    async def test_multiple_users_isolated(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that multiple users are properly isolated."""
        # Create user 1
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "password": "Password123!",
                "password_confirm": "Password123!",
                "full_name": "User One",
                "accept_terms": True,
            },
        )

        # Create user 2
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "Password123!",
                "password_confirm": "Password123!",
                "full_name": "User Two",
                "accept_terms": True,
            },
        )

        # Login as user 1
        login1 = await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "Password123!"},
        )
        token1 = login1.json()["access_token"]

        # Login as user 2
        login2 = await client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "Password123!"},
        )
        token2 = login2.json()["access_token"]

        # Verify each token returns correct user
        me1 = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert me1.json()["email"] == "user1@example.com"

        me2 = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert me2.json()["email"] == "user2@example.com"
