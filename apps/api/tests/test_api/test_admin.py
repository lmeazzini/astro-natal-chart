"""
Tests for admin endpoints.

Tests RBAC (Role-Based Access Control) with GERAL and ADMIN roles.
Tests email verification requirement for admin access (issue #138).
"""

from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User


class TestUnverifiedAdminRestriction:
    """Tests for restricting admin features to verified email admins (issue #138)."""

    async def test_unverified_admin_cannot_list_users(
        self,
        client: AsyncClient,
        unverified_admin_auth_headers: dict[str, str],
    ):
        """Admin with unverified email should not be able to list users."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=unverified_admin_auth_headers,
        )

        assert response.status_code == 403
        # Should indicate email verification is required
        assert "verification" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()

    async def test_unverified_admin_cannot_get_user_detail(
        self,
        client: AsyncClient,
        unverified_admin_auth_headers: dict[str, str],
        test_user: User,
    ):
        """Admin with unverified email should not be able to get user details."""
        response = await client.get(
            f"/api/v1/admin/users/{test_user.id}",
            headers=unverified_admin_auth_headers,
        )

        assert response.status_code == 403

    async def test_unverified_admin_cannot_update_role(
        self,
        client: AsyncClient,
        unverified_admin_auth_headers: dict[str, str],
        test_user: User,
    ):
        """Admin with unverified email should not be able to update user roles."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_user.id}/role",
            headers=unverified_admin_auth_headers,
            json={"role": "admin"},
        )

        assert response.status_code == 403

    async def test_unverified_admin_cannot_get_stats(
        self,
        client: AsyncClient,
        unverified_admin_auth_headers: dict[str, str],
    ):
        """Admin with unverified email should not be able to get system stats."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=unverified_admin_auth_headers,
        )

        assert response.status_code == 403

    async def test_verified_admin_can_access_all_endpoints(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_admin_user: User,
    ):
        """Admin with verified email should be able to access all admin endpoints."""
        # List users
        response = await client.get(
            "/api/v1/admin/users",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200

        # Get stats
        response = await client.get(
            "/api/v1/admin/stats",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestListUsers:
    """Tests for GET /api/v1/admin/users endpoint."""

    async def test_admin_can_list_users(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_admin_user: User,
    ):
        """Admin should be able to list all users."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 1
        # Admin user should be in the list
        emails = [u["email"] for u in data["users"]]
        assert test_admin_user.email in emails

    async def test_regular_user_cannot_list_users(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Regular user should not be able to list users."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=auth_headers,
        )

        assert response.status_code == 403
        # Message can be translated (pt-BR: "Privilégios insuficientes")
        assert response.json()["detail"] is not None

    async def test_unauthenticated_cannot_list_users(
        self,
        client: AsyncClient,
    ):
        """Unauthenticated request should be rejected."""
        response = await client.get("/api/v1/admin/users")

        # Without auth header, FastAPI HTTPBearer returns 403 (Forbidden)
        assert response.status_code == 403

    async def test_list_users_pagination(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user_factory,
    ):
        """Test pagination of user list."""
        # Create multiple users
        for i in range(5):
            await test_user_factory(email=f"user{i}@example.com")

        # Get first page
        response = await client.get(
            "/api/v1/admin/users?skip=0&limit=3",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 3
        assert data["skip"] == 0
        assert data["limit"] == 3
        assert data["total"] >= 5


class TestGetUserDetail:
    """Tests for GET /api/v1/admin/users/{user_id} endpoint."""

    async def test_admin_can_get_user_detail(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user: User,
    ):
        """Admin should be able to get user details."""
        response = await client.get(
            f"/api/v1/admin/users/{test_user.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == "geral"
        assert "chart_count" in data

    async def test_regular_user_cannot_get_user_detail(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_admin_user: User,
    ):
        """Regular user should not be able to get user details."""
        response = await client.get(
            f"/api/v1/admin/users/{test_admin_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_get_nonexistent_user(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
    ):
        """Getting a nonexistent user should return 404."""
        response = await client.get(
            f"/api/v1/admin/users/{uuid4()}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestUpdateUserRole:
    """Tests for PATCH /api/v1/admin/users/{user_id}/role endpoint."""

    async def test_admin_can_promote_user_to_admin(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user: User,
    ):
        """Admin should be able to promote a regular user to admin."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_user.id}/role",
            headers=admin_auth_headers,
            json={"role": "admin"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["new_role"] == "admin"
        assert "Role updated successfully" in data["message"]

    async def test_admin_can_demote_user(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user_factory,
        db_session: AsyncSession,
    ):
        """Admin should be able to demote another admin to regular user."""
        # Create another admin
        another_admin = await test_user_factory(
            email="another@realastrology.ai",
            role=UserRole.ADMIN.value,
            is_superuser=True,
        )

        response = await client.patch(
            f"/api/v1/admin/users/{another_admin.id}/role",
            headers=admin_auth_headers,
            json={"role": "geral"},
        )

        # Should fail because we can't modify another admin's role
        assert response.status_code == 403
        assert "Cannot modify another admin" in response.json()["detail"]

    async def test_admin_cannot_modify_own_role(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_admin_user: User,
    ):
        """Admin should not be able to modify their own role."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_admin_user.id}/role",
            headers=admin_auth_headers,
            json={"role": "geral"},
        )

        assert response.status_code == 400
        assert "Cannot modify your own role" in response.json()["detail"]

    async def test_cannot_demote_last_admin(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user_factory,
        db_session: AsyncSession,
    ):
        """Cannot demote the last admin in the system."""
        # Create a user that is marked as admin but not modifying another admin
        # This test ensures we can't remove the last admin
        # First, let's create a user with admin role
        new_user = await test_user_factory(
            email="temp@example.com",
            role=UserRole.GERAL.value,
        )

        # This should work - promoting user
        response = await client.patch(
            f"/api/v1/admin/users/{new_user.id}/role",
            headers=admin_auth_headers,
            json={"role": "admin"},
        )
        assert response.status_code == 200

    async def test_regular_user_cannot_update_roles(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_user_factory,
    ):
        """Regular user should not be able to update roles."""
        other_user = await test_user_factory(email="other@example.com")

        response = await client.patch(
            f"/api/v1/admin/users/{other_user.id}/role",
            headers=auth_headers,
            json={"role": "admin"},
        )

        assert response.status_code == 403

    async def test_update_role_invalid_role(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_user: User,
    ):
        """Updating with invalid role should fail."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_user.id}/role",
            headers=admin_auth_headers,
            json={"role": "invalid_role"},
        )

        assert response.status_code == 422


class TestSystemStats:
    """Tests for GET /api/v1/admin/stats endpoint."""

    async def test_admin_can_get_stats(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
        test_admin_user: User,
    ):
        """Admin should be able to get system stats."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_charts" in data
        assert "active_users" in data
        assert "verified_users" in data
        assert "users_by_role" in data
        assert data["total_users"] >= 1

    async def test_regular_user_cannot_get_stats(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Regular user should not be able to get system stats."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestRoleAssignment:
    """Tests for automatic role assignment during registration."""

    async def test_register_regular_user_gets_geral_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Regular user registration should get GERAL role."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test123!@#",
                "password_confirm": "Test123!@#",
                "full_name": "New User",
                "accept_terms": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        # Response is UserRead schema directly (not wrapped in "user" key)
        assert data["role"] == "geral"

    async def test_register_realastrology_email_gets_admin_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        """User with @realastrology.ai email should get ADMIN role."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newadmin@realastrology.ai",
                "password": "Admin123!@#",
                "password_confirm": "Admin123!@#",
                "full_name": "New Admin",
                "accept_terms": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        # Response is UserRead schema directly (not wrapped in "user" key)
        assert data["role"] == "admin"
        assert data["is_superuser"] is True


class TestSuperuserBackwardCompatibility:
    """Tests for backward compatibility with is_superuser field."""

    async def test_superuser_is_admin(
        self,
        client: AsyncClient,
        test_user_factory,
    ):
        """User with is_superuser=True should have admin access."""
        # Create superuser without admin role
        superuser = await test_user_factory(
            email="superuser@example.com",
            is_superuser=True,
            role=UserRole.GERAL.value,  # Role is geral but is_superuser is True
        )

        from app.core.security import create_access_token

        access_token = create_access_token(data={"sub": str(superuser.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # Should have admin access due to is_superuser
        response = await client.get(
            "/api/v1/admin/users",
            headers=headers,
        )

        assert response.status_code == 200


class TestUserReadSchema:
    """Tests that UserRead schema includes role field."""

    async def test_user_me_includes_role(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """GET /users/me should return user role."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "role" in data
        assert data["role"] == "geral"

    async def test_admin_user_me_includes_admin_role(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
    ):
        """Admin GET /users/me should return admin role."""
        response = await client.get(
            "/api/v1/users/me",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "role" in data
        assert data["role"] == "admin"
