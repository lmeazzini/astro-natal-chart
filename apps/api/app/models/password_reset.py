"""
Model for password reset tokens.
"""

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PasswordResetToken(Base):
    """
    Token para recuperação de senha.

    Attributes:
        id: UUID único do token
        user_id: FK para usuário
        token: Hash SHA256 do token (64 chars)
        expires_at: Data/hora de expiração (1 hora após criação)
        used: Flag indicando se token já foi usado
        created_at: Data/hora de criação
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    @property
    def is_valid(self) -> bool:
        """
        Verifica se token é válido (não expirado e não usado).

        Returns:
            True se token ainda é válido, False caso contrário
        """
        return not self.used and datetime.utcnow() < self.expires_at

    @property
    def is_expired(self) -> bool:
        """Verifica se token está expirado."""
        return datetime.utcnow() >= self.expires_at

    def __repr__(self) -> str:
        """String representation."""
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used}, expires_at={self.expires_at})>"
