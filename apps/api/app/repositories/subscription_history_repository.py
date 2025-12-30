"""Repository for SubscriptionHistory model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription_history import SubscriptionHistory
from app.repositories.base import BaseRepository


class SubscriptionHistoryRepository(BaseRepository[SubscriptionHistory]):
    """Repository for SubscriptionHistory model."""

    def __init__(self, db: AsyncSession):
        """Initialize SubscriptionHistory repository."""
        super().__init__(SubscriptionHistory, db)

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[SubscriptionHistory]:
        """Get subscription history for a user, ordered by created_at descending."""
        stmt = (
            select(SubscriptionHistory)
            .where(SubscriptionHistory.user_id == user_id)
            .order_by(SubscriptionHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_subscription_id(self, subscription_id: UUID) -> list[SubscriptionHistory]:
        """Get all history records for a subscription, ordered by created_at."""
        stmt = (
            select(SubscriptionHistory)
            .where(SubscriptionHistory.subscription_id == subscription_id)
            .order_by(SubscriptionHistory.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count total history records for a user."""
        from sqlalchemy import func

        stmt = select(func.count()).where(SubscriptionHistory.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
