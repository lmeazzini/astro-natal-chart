"""Subscription history model for tracking all subscription changes over time."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.user import User


class SubscriptionHistory(Base):
    """Immutable record of subscription state changes.

    Each row represents a snapshot of the subscription at the time of a change.
    Used for analytics, auditing, and tracking subscription lifecycle.
    """

    __tablename__ = "subscription_history"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    subscription_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Snapshot of subscription state at this point in time
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Change metadata
    change_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    changed_by_user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    change_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamp (immutable - no updated_at)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        foreign_keys=[subscription_id],
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )

    changed_by: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[changed_by_user_id],
    )
