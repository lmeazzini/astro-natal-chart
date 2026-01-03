"""Webhook event model for Stripe event idempotency."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WebhookEvent(Base):
    """Record of processed Stripe webhook events for idempotency."""

    __tablename__ = "webhook_events"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Stripe event identifier (unique for idempotency)
    stripe_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Event type (e.g., checkout.session.completed)
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Processing status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
        comment="pending, processed, failed",
    )

    # Full event payload (for debugging/replay)
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Error information if processing failed
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
