"""
User and OAuth Account repositories.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import OAuthAccount, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: AsyncSession):
        """Initialize User repository."""
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        user = await self.get_by_email(email)
        return user is not None

    async def get_active_user_by_id(self, user_id: UUID) -> User | None:
        """
        Get active user by ID.

        Args:
            user_id: User UUID

        Returns:
            User instance or None if not found or inactive
        """
        stmt = select(User).where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_user_by_email(self, email: str) -> User | None:
        """
        Get active user by email.

        Args:
            email: User email

        Returns:
            User instance or None if not found or inactive
        """
        stmt = select(User).where(
            User.email == email,
            User.is_active == True,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, user: User) -> User:
        """
        Soft delete user by setting deleted_at timestamp.

        Args:
            user: User instance to soft delete

        Returns:
            Updated user instance
        """
        user.deleted_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_with_oauth_accounts(self, user_id: UUID) -> User | None:
        """
        Get user by ID with OAuth accounts eagerly loaded.

        Args:
            user_id: User UUID

        Returns:
            User instance with OAuth accounts or None if not found
        """
        stmt = select(User).where(User.id == user_id).options(selectinload(User.oauth_accounts))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    """Repository for OAuth Account model."""

    def __init__(self, db: AsyncSession):
        """Initialize OAuth Account repository."""
        super().__init__(OAuthAccount, db)

    async def get_by_provider_and_user_id(
        self,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount | None:
        """
        Get OAuth account by provider and provider user ID.

        Args:
            provider: OAuth provider (google, github, facebook)
            provider_user_id: User ID from provider

        Returns:
            OAuth account instance or None if not found
        """
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> list[OAuthAccount]:
        """
        Get all OAuth accounts for a user.

        Args:
            user_id: User UUID

        Returns:
            List of OAuth accounts
        """
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def exists_for_provider(
        self,
        provider: str,
        provider_user_id: str,
    ) -> bool:
        """
        Check if OAuth account exists for provider.

        Args:
            provider: OAuth provider
            provider_user_id: User ID from provider

        Returns:
            True if account exists, False otherwise
        """
        account = await self.get_by_provider_and_user_id(provider, provider_user_id)
        return account is not None
