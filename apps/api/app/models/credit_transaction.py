"""CreditTransaction model for tracking credit usage and changes."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TransactionType

if TYPE_CHECKING:
    from app.models.user import User


class CreditTransaction(Base):
    """Immutable record of credit transactions.

    Each row represents a change to a user's credit balance.
    Used for auditing, analytics, and usage tracking.
    """

    __tablename__ = "credit_transactions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction type
    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    # Amount (positive for credits added, negative for debits)
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Balance after this transaction
    balance_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Feature that consumed credits (for DEBIT transactions)
    feature_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # Resource ID that triggered the transaction (e.g., chart_id)
    resource_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        nullable=True,
    )

    # Human-readable description
    description: Mapped[str | None] = mapped_column(
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
    user: Mapped["User"] = relationship("User")

    # Computed properties
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction (credits consumed)."""
        return self.transaction_type == TransactionType.DEBIT.value

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction (credits added)."""
        return self.transaction_type in [
            TransactionType.CREDIT.value,
            TransactionType.RESET.value,
            TransactionType.UPGRADE.value,
            TransactionType.BONUS.value,
        ]

    def __repr__(self) -> str:
        return f"<CreditTransaction user_id={self.user_id} type={self.transaction_type} amount={self.amount}>"
