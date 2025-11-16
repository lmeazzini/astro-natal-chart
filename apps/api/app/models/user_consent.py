"""
Model for user consent tracking (LGPD/GDPR compliance).
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserConsent(Base):
    """
    Rastreamento de consentimentos do usuário (LGPD/GDPR).

    Attributes:
        id: UUID único do registro
        user_id: FK para usuário
        consent_type: Tipo de consentimento (terms, privacy, cookies, marketing)
        version: Versão do documento aceito (ex: "1.0", "2024-11-15")
        accepted: Se o consentimento foi dado ou revogado
        ip_address: IP do usuário no momento do consentimento
        user_agent: User agent do navegador
        consent_text: Texto do consentimento no momento da aceitação (opcional)
        created_at: Data/hora do consentimento
        revoked_at: Data/hora de revogação (se aplicável)
    """

    __tablename__ = "user_consents"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: terms, privacy, cookies, marketing",
    )
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Document version (e.g., '1.0', '2024-11-15')",
    )
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="IPv4 or IPv6 address")
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Browser user agent string")
    consent_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Snapshot of consent text at acceptance time",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_active(self) -> bool:
        """Verifica se consentimento está ativo (aceito e não revogado)."""
        return self.accepted and self.revoked_at is None

    def revoke(self) -> None:
        """Revoga o consentimento."""
        self.accepted = False
        self.revoked_at = datetime.utcnow()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<UserConsent(user_id={self.user_id}, "
            f"type={self.consent_type}, "
            f"version={self.version}, "
            f"accepted={self.accepted})>"
        )
