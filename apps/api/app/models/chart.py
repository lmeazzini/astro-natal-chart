"""
Birth Chart model for database.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interpretation import ChartInterpretation
    from app.models.user import User


class BirthChart(Base):
    """Birth chart model."""

    __tablename__ = "birth_charts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    person_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Birth information
    birth_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    birth_timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # User notes and organization
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)), nullable=True)

    # Calculation settings
    house_system: Mapped[str] = mapped_column(String(20), default="placidus", nullable=False)
    zodiac_type: Mapped[str] = mapped_column(String(20), default="tropical", nullable=False)
    node_type: Mapped[str] = mapped_column(String(20), default="true", nullable=False)

    # Async processing status (for Celery background tasks)
    status: Mapped[str] = mapped_column(
        String(20),
        default="processing",
        nullable=False,
        index=True,
    )  # processing, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Calculated chart data (stored as JSONB for flexibility)
    chart_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Sharing and visibility
    visibility: Mapped[str] = mapped_column(String(20), default="private", nullable=False)
    share_uuid: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
        index=True,
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="birth_charts")  # noqa: F821
    interpretations: Mapped[list["ChartInterpretation"]] = relationship(  # noqa: F821
        "ChartInterpretation",
        back_populates="chart",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BirthChart {self.person_name} ({self.id})>"


class AuditLog(Base):
    """Audit log model for LGPD/GDPR compliance."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} at {self.created_at}>"
