"""UserCredit model for tracking user credit balance."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PlanType

if TYPE_CHECKING:
    from app.models.user import User


class UserCredit(Base):
    """User credit balance tracking model.

    Each user has one credit record that tracks their current balance,
    plan type, and billing period for credit reset.
    """

    __tablename__ = "user_credits"

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
        unique=True,  # One credit record per user
        nullable=False,
        index=True,
    )

    # Plan type determines credit allocation
    plan_type: Mapped[str] = mapped_column(
        String(20),
        default=PlanType.FREE.value,
        nullable=False,
        index=True,
    )

    # Current credit balance
    credits_balance: Mapped[int] = mapped_column(
        Integer,
        default=10,  # Free tier default
        nullable=False,
    )

    # Purchased credits (one-time purchases, never expire)
    purchased_credits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Monthly credit limit (NULL = unlimited for UNLIMITED plan)
    credits_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Billing period for credit reset
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Period end (NULL = never expires for free tier)
    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
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
    user: Mapped["User"] = relationship("User", back_populates="credits")

    # Computed properties
    @property
    def is_unlimited(self) -> bool:
        """Check if user has unlimited credits."""
        return self.credits_limit is None

    @property
    def is_period_expired(self) -> bool:
        """Check if the current billing period has expired."""
        if self.period_end is None:
            return False  # Free tier never expires
        return datetime.now(UTC) >= self.period_end

    @property
    def days_until_reset(self) -> int | None:
        """Calculate days until credit reset (None if no reset scheduled)."""
        if self.period_end is None:
            return None
        delta = self.period_end - datetime.now(UTC)
        return max(0, delta.days)

    @property
    def credits_used(self) -> int:
        """Calculate credits used in current period."""
        if self.credits_limit is None:
            return 0  # Unlimited plans don't track usage
        return max(0, self.credits_limit - self.credits_balance)

    @property
    def usage_percentage(self) -> float:
        """Calculate credit usage percentage (0-100)."""
        if self.credits_limit is None or self.credits_limit == 0:
            return 0.0
        return min(100.0, (self.credits_used / self.credits_limit) * 100)

    def __repr__(self) -> str:
        return f"<UserCredit user_id={self.user_id} plan={self.plan_type} balance={self.credits_balance}>"
