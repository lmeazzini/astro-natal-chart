"""Repository for UserCredit data access."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_credit import UserCredit
from app.repositories.base import BaseRepository


class CreditRepository(BaseRepository[UserCredit]):
    """Repository for UserCredit operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with UserCredit model."""
        super().__init__(UserCredit, db)

    async def get_by_user_id(self, user_id: UUID) -> UserCredit | None:
        """
        Get credit record by user ID.

        Args:
            user_id: User UUID

        Returns:
            UserCredit instance or None if not found
        """
        stmt = select(UserCredit).where(UserCredit.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users_needing_reset(
        self,
        before_date: datetime,
        limit: int = 100,
    ) -> list[UserCredit]:
        """
        Get users whose credit period has expired.

        Args:
            before_date: Get users with period_end before this date
            limit: Maximum number of records to return

        Returns:
            List of UserCredit records needing reset
        """
        stmt = (
            select(UserCredit)
            .where(
                UserCredit.period_end.isnot(None),
                UserCredit.period_end < before_date,
            )
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_plan_type(
        self,
        plan_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserCredit]:
        """
        Get all credit records by plan type.

        Args:
            plan_type: Plan type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of UserCredit records
        """
        stmt = select(UserCredit).where(UserCredit.plan_type == plan_type).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_plan_type(self, plan_type: str) -> int:
        """
        Count users by plan type.

        Args:
            plan_type: Plan type to count

        Returns:
            Number of users with this plan type
        """
        from sqlalchemy import func

        stmt = select(func.count()).where(UserCredit.plan_type == plan_type)
        result = await self.db.execute(stmt)
        return result.scalar_one()
