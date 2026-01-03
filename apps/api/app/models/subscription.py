"""Subscription model for tracking premium user subscriptions."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PlanType, SubscriptionStatus

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.user import User


class Subscription(Base):
    """User subscription tracking model."""

    __tablename__ = "subscriptions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign key to user (one-to-one relationship)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # One subscription per user
        nullable=False,
        index=True,
    )

    # Subscription status
    status: Mapped[str] = mapped_column(
        String(20),
        default=SubscriptionStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    # Plan type (for credits system)
    plan_type: Mapped[str] = mapped_column(
        String(50),
        default=PlanType.FREE.value,
        nullable=False,
        index=True,
    )

    # Stripe integration fields
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    stripe_price_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Stripe billing period
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Cancellation flag
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Dates (timezone-aware)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,  # NULL = lifetime premium (partnerships, contests)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")

    # Computed properties
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != SubscriptionStatus.ACTIVE.value:
            return False
        if self.expires_at is None:
            return True  # Lifetime premium
        return datetime.now(UTC) < self.expires_at

    @property
    def is_expired(self) -> bool:
        """Check if subscription has expired."""
        if self.expires_at is None:
            return False  # Never expires
        return datetime.now(UTC) >= self.expires_at

    @property
    def days_remaining(self) -> int | None:
        """Calculate days until expiration (None if lifetime)."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(UTC)
        return max(0, delta.days)
