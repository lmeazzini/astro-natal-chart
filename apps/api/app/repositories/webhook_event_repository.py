"""Repository for WebhookEvent model operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_event import WebhookEvent
from app.repositories.base import BaseRepository


class WebhookEventRepository(BaseRepository[WebhookEvent]):
    """Repository for WebhookEvent database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(WebhookEvent, db)

    async def get_by_stripe_event_id(self, stripe_event_id: str) -> WebhookEvent | None:
        """Get webhook event by Stripe event ID for idempotency check."""
        stmt = select(WebhookEvent).where(WebhookEvent.stripe_event_id == stripe_event_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def event_already_processed(self, stripe_event_id: str) -> bool:
        """Check if a webhook event has already been processed."""
        event = await self.get_by_stripe_event_id(stripe_event_id)
        return event is not None and event.status == "processed"

    async def mark_as_processed(self, stripe_event_id: str) -> WebhookEvent | None:
        """Mark a webhook event as processed."""
        event = await self.get_by_stripe_event_id(stripe_event_id)
        if event:
            event.status = "processed"
            event.processed_at = datetime.now(UTC)
            await self.db.flush()
        return event

    async def mark_as_failed(self, stripe_event_id: str, error_message: str) -> WebhookEvent | None:
        """Mark a webhook event as failed with error message."""
        event = await self.get_by_stripe_event_id(stripe_event_id)
        if event:
            event.status = "failed"
            event.error_message = error_message
            event.processed_at = datetime.now(UTC)
            await self.db.flush()
        return event

    async def get_failed_events(self, limit: int = 100) -> list[WebhookEvent]:
        """Get failed webhook events for retry."""
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.status == "failed")
            .order_by(WebhookEvent.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_events(self, limit: int = 100) -> list[WebhookEvent]:
        """Get pending webhook events."""
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.status == "pending")
            .order_by(WebhookEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
