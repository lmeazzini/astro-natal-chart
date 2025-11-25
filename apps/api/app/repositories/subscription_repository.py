"""Repository for Subscription model."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription model."""

    def __init__(self, db: AsyncSession):
        """Initialize Subscription repository."""
        super().__init__(Subscription, db)

    async def get_by_user_id(self, user_id: UUID) -> Subscription | None:
        """Get subscription by user ID."""
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_active(self, skip: int = 0, limit: int = 100) -> list[Subscription]:
        """Get all active subscriptions."""
        stmt = select(Subscription).where(Subscription.status == "active").offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_expired_subscriptions(self) -> list[Subscription]:
        """Get subscriptions that have expired but status is still 'active'."""
        now = datetime.now(UTC)
        stmt = select(Subscription).where(
            Subscription.status == "active",
            Subscription.expires_at.isnot(None),
            Subscription.expires_at < now,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
