"""Payment model for tracking Stripe payments."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.user import User


class Payment(Base):
    """Record of payments processed through Stripe."""

    __tablename__ = "payments"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subscription_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Stripe identifiers
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    stripe_invoice_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    stripe_charge_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    # Payment details
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Amount in cents",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="brl",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="succeeded, pending, failed, refunded",
    )

    # Receipt and description
    receipt_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="payments"
    )

    @property
    def amount_display(self) -> str:
        """Format amount for display (e.g., R$ 19,90)."""
        if self.currency.lower() == "brl":
            return (
                f"R$ {self.amount / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        return f"{self.currency.upper()} {self.amount / 100:.2f}"
