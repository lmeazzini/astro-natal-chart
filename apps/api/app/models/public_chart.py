"""
Public Chart model for famous people's birth charts.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import ARRAY, Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PublicChart(Base):
    """Public chart model for famous people's natal charts."""

    __tablename__ = "public_charts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # URL-friendly identifier
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Basic info
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )  # scientist, artist, leader, writer, athlete, etc.

    # Birth information
    birth_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    birth_timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Calculated chart data (stored as JSONB for flexibility)
    chart_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    house_system: Mapped[str] = mapped_column(
        String(50),
        default="placidus",
        nullable=False,
    )

    # Content
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )  # Array of astrological insights

    # SEO
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(100)),
        nullable=True,
    )

    # Stats
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Flags
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
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

    def __repr__(self) -> str:
        return f"<PublicChart {self.full_name} ({self.slug})>"
