"""
Tests for the require_premium dependency.

This dependency ensures that only premium or admin users can access
premium features like horary astrology, profections, firdaria, etc.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.enums import UserRole
from app.models.user import User

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def free_user(db_session: AsyncSession) -> User:
    """Create a user with FREE role."""
    user = User(
        id=uuid4(),
        email="free@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Free User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        role=UserRole.FREE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def free_user_headers(free_user: User) -> dict[str, str]:
    """Get auth headers for free user."""
    access_token = create_access_token(data={"sub": str(free_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def premium_user(db_session: AsyncSession) -> User:
    """Create a user with PREMIUM role."""
    user = User(
        id=uuid4(),
        email="premium@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Premium User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        role=UserRole.PREMIUM.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def premium_user_headers(premium_user: User) -> dict[str, str]:
    """Get auth headers for premium user."""
    access_token = create_access_token(data={"sub": str(premium_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create a user with ADMIN role."""
    user = User(
        id=uuid4(),
        email="admin@realastrology.ai",
        password_hash=get_password_hash("Admin123!@#"),
        full_name="Admin User",
        email_verified=True,
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user_headers(admin_user: User) -> dict[str, str]:
    """Get auth headers for admin user."""
    access_token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


# =============================================================================
# Unit Tests for User.is_premium property
# =============================================================================


class TestIsPremiumProperty:
    """Test the User.is_premium property."""

    async def test_free_user_is_not_premium(self, free_user: User) -> None:
        """Free users should NOT be considered premium."""
        assert free_user.is_premium is False

    async def test_premium_user_is_premium(self, premium_user: User) -> None:
        """Premium users should be considered premium."""
        assert premium_user.is_premium is True

    async def test_admin_user_is_premium(self, admin_user: User) -> None:
        """Admin users should be considered premium (they have all access)."""
        assert admin_user.is_premium is True

    async def test_superuser_is_premium(self, db_session: AsyncSession) -> None:
        """Superusers should be considered premium regardless of role."""
        user = User(
            id=uuid4(),
            email="superuser@example.com",
            password_hash=get_password_hash("Test123!@#"),
            full_name="Superuser",
            email_verified=True,
            is_active=True,
            is_superuser=True,  # Superuser flag
            role=UserRole.FREE.value,  # FREE role but superuser
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Even with FREE role, superuser should be considered premium
        assert user.is_premium is True


class TestIsAdminProperty:
    """Test the User.is_admin property."""

    async def test_free_user_is_not_admin(self, free_user: User) -> None:
        """Free users should NOT be considered admin."""
        assert free_user.is_admin is False

    async def test_premium_user_is_not_admin(self, premium_user: User) -> None:
        """Premium users should NOT be considered admin."""
        assert premium_user.is_admin is False

    async def test_admin_user_is_admin(self, admin_user: User) -> None:
        """Admin users should be considered admin."""
        assert admin_user.is_admin is True


class TestUserRoleProperty:
    """Test the User.user_role property."""

    async def test_free_user_role(self, free_user: User) -> None:
        """Free user should return FREE role enum."""
        assert free_user.user_role == UserRole.FREE

    async def test_premium_user_role(self, premium_user: User) -> None:
        """Premium user should return PREMIUM role enum."""
        assert premium_user.user_role == UserRole.PREMIUM

    async def test_admin_user_role(self, admin_user: User) -> None:
        """Admin user should return ADMIN role enum."""
        assert admin_user.user_role == UserRole.ADMIN

    async def test_invalid_role_returns_free(self, db_session: AsyncSession) -> None:
        """User with invalid role should return FREE as fallback."""
        user = User(
            id=uuid4(),
            email="invalid@example.com",
            password_hash=get_password_hash("Test123!@#"),
            full_name="Invalid Role User",
            email_verified=True,
            is_active=True,
            is_superuser=False,
            role="invalid_role",  # Invalid role
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Should fallback to FREE
        assert user.user_role == UserRole.FREE


# =============================================================================
# Integration Tests for require_premium dependency
# =============================================================================
# Note: These tests require an endpoint that uses require_premium.
# Since no endpoint uses it yet, we test the dependency directly.


class TestRequirePremiumDependency:
    """Test the require_premium dependency function directly."""

    async def test_require_premium_blocks_free_user(
        self, free_user: User
    ) -> None:
        """require_premium should raise 403 for free users."""
        from fastapi import HTTPException

        from app.core.dependencies import require_premium

        # Mock the dependency by passing the user directly
        # The dependency signature expects Annotated[User, Depends(get_current_user)]
        # but we can test the logic directly
        with pytest.raises(HTTPException) as exc_info:
            await require_premium(free_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "premium_required"

    async def test_require_premium_allows_premium_user(
        self, premium_user: User
    ) -> None:
        """require_premium should allow premium users."""
        from app.core.dependencies import require_premium

        result = await require_premium(premium_user)
        assert result == premium_user

    async def test_require_premium_allows_admin_user(
        self, admin_user: User
    ) -> None:
        """require_premium should allow admin users."""
        from app.core.dependencies import require_premium

        result = await require_premium(admin_user)
        assert result == admin_user


# =============================================================================
# Tests for UserRole enum
# =============================================================================


class TestUserRoleEnum:
    """Test the UserRole enum values."""

    def test_role_values(self) -> None:
        """Verify correct string values for roles."""
        assert UserRole.FREE.value == "free"
        assert UserRole.PREMIUM.value == "premium"
        assert UserRole.ADMIN.value == "admin"

    def test_role_str(self) -> None:
        """Verify __str__ returns the value."""
        assert str(UserRole.FREE) == "free"
        assert str(UserRole.PREMIUM) == "premium"
        assert str(UserRole.ADMIN) == "admin"
