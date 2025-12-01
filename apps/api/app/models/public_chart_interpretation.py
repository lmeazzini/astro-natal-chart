"""
Public Chart Interpretation model for storing AI-generated interpretations
of famous people's birth charts.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.public_chart import PublicChart


class PublicChartInterpretation(Base):
    """AI-generated interpretation for public chart elements."""

    __tablename__ = "public_chart_interpretations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    chart_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public_charts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interpretation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Type: 'planet', 'house', 'aspect', or 'arabic_part'",
    )
    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g., 'Sun', '1', 'Sun-Trine-Moon', 'fortune'",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="AI-generated interpretation text",
    )
    openai_model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="OpenAI model used (e.g., 'gpt-4o-mini')",
    )
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Prompt version for tracking changes",
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="pt-BR",
        index=True,
        comment="Language code (pt-BR or en-US)",
    )
    rag_sources: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="RAG document sources used for this interpretation",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    chart: Mapped["PublicChart"] = relationship(
        "PublicChart",
        back_populates="interpretations",
    )

    def __repr__(self) -> str:
        return f"<PublicChartInterpretation {self.interpretation_type}:{self.subject}>"
