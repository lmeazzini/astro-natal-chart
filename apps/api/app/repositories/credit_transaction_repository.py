"""Repository for CreditTransaction data access."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credit_transaction import CreditTransaction
from app.repositories.base import BaseRepository


class CreditTransactionRepository(BaseRepository[CreditTransaction]):
    """Repository for CreditTransaction operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with CreditTransaction model."""
        super().__init__(CreditTransaction, db)

    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CreditTransaction]:
        """
        Get transactions for a user, ordered by most recent first.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of CreditTransaction records
        """
        stmt = (
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: UUID) -> int:
        """
        Count transactions for a user.

        Args:
            user_id: User UUID

        Returns:
            Total number of transactions
        """
        stmt = select(func.count()).where(CreditTransaction.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_usage_by_feature(
        self,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        """
        Get credit usage breakdown by feature type.

        Args:
            user_id: User UUID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary mapping feature_type to total credits consumed
        """
        from app.models.enums import TransactionType

        stmt = (
            select(
                CreditTransaction.feature_type,
                func.sum(func.abs(CreditTransaction.amount)).label("total"),
            )
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == TransactionType.DEBIT.value,
                CreditTransaction.feature_type.isnot(None),
            )
            .group_by(CreditTransaction.feature_type)
        )

        if start_date:
            stmt = stmt.where(CreditTransaction.created_at >= start_date)
        if end_date:
            stmt = stmt.where(CreditTransaction.created_at < end_date)

        result = await self.db.execute(stmt)
        rows = result.all()
        return {row.feature_type: int(row.total) for row in rows}

    async def get_recent_debits(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[CreditTransaction]:
        """
        Get recent debit transactions for a user.

        Args:
            user_id: User UUID
            limit: Maximum number of records to return

        Returns:
            List of recent debit transactions
        """
        from app.models.enums import TransactionType

        stmt = (
            select(CreditTransaction)
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == TransactionType.DEBIT.value,
            )
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_transactions_in_period(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CreditTransaction]:
        """
        Get all transactions within a specific period.

        Args:
            user_id: User UUID
            start_date: Period start (inclusive)
            end_date: Period end (exclusive)

        Returns:
            List of transactions in the period
        """
        stmt = (
            select(CreditTransaction)
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.created_at >= start_date,
                CreditTransaction.created_at < end_date,
            )
            .order_by(CreditTransaction.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_unlocked_features_for_chart(
        self,
        user_id: UUID,
        chart_id: UUID,
    ) -> list[str]:
        """
        Get distinct feature types that have been paid for a specific chart.

        Args:
            user_id: User UUID
            chart_id: Chart UUID (stored as resource_id)

        Returns:
            List of unique feature_type strings that were unlocked
        """
        from app.models.enums import TransactionType

        stmt = (
            select(CreditTransaction.feature_type)
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.resource_id == chart_id,
                CreditTransaction.transaction_type == TransactionType.DEBIT.value,
                CreditTransaction.feature_type.isnot(None),
            )
            .distinct()
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_solar_return_transactions_for_chart(
        self,
        user_id: UUID,
        chart_id: UUID,
    ) -> list[CreditTransaction]:
        """
        Get Solar Return transactions for a specific chart.

        Used to extract which years have been paid for.

        Args:
            user_id: User UUID
            chart_id: Chart UUID

        Returns:
            List of Solar Return transactions
        """
        from app.models.enums import FeatureType, TransactionType

        stmt = (
            select(CreditTransaction)
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.resource_id == chart_id,
                CreditTransaction.transaction_type == TransactionType.DEBIT.value,
                CreditTransaction.feature_type == FeatureType.SOLAR_RETURN.value,
            )
            .order_by(CreditTransaction.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def has_feature_unlocked(
        self,
        user_id: UUID,
        chart_id: UUID,
        feature_type: str,
    ) -> bool:
        """
        Check if a feature has been unlocked (paid) for a specific chart.

        Args:
            user_id: User UUID
            chart_id: Chart UUID
            feature_type: Feature type to check

        Returns:
            True if feature was previously paid for, False otherwise
        """
        from app.models.enums import TransactionType

        stmt = select(func.count()).where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.resource_id == chart_id,
            CreditTransaction.transaction_type == TransactionType.DEBIT.value,
            CreditTransaction.feature_type == feature_type,
        )
        result = await self.db.execute(stmt)
        count = result.scalar_one()
        return count > 0
