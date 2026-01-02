"""Repository for Payment model operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Payment, db)

    async def get_by_stripe_payment_intent(self, payment_intent_id: str) -> Payment | None:
        """Get payment by Stripe payment intent ID."""
        stmt = select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_stripe_invoice(self, invoice_id: str) -> Payment | None:
        """Get payment by Stripe invoice ID."""
        stmt = select(Payment).where(Payment.stripe_invoice_id == invoice_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_payments(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Payment]:
        """Get paginated payments for a user."""
        stmt = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_subscription_payments(
        self,
        subscription_id: UUID,
        limit: int = 50,
    ) -> list[Payment]:
        """Get payments for a subscription."""
        stmt = (
            select(Payment)
            .where(Payment.subscription_id == subscription_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
