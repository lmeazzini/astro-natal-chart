"""
Service for password reset functionality.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.services.email import EmailService


class PasswordResetService:
    """Service para gerenciar recuperação de senha."""

    TOKEN_EXPIRY_HOURS = 1
    TOKEN_LENGTH = 32  # 32 bytes = 64 chars hex

    def __init__(self, email_service: EmailService | None = None):
        """
        Inicializa o serviço.

        Args:
            email_service: Serviço de email (opcional, para testes)
        """
        self.email_service = email_service or EmailService()

    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str,
    ) -> dict[str, str | bool]:
        """
        Solicita recuperação de senha.

        Gera token, salva no banco, envia email.
        SEMPRE retorna sucesso mesmo se email não existe (segurança).

        Args:
            db: Sessão do banco de dados
            email: Email do usuário

        Returns:
            Dict com mensagem de sucesso e flag de sucesso
        """
        # Buscar usuário
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        # Se usuário não existe, retorna sucesso (não revelar)
        if not user:
            return {
                "message": "Se o email existir, você receberá instruções de recuperação",
                "success": True,
            }

        # Gerar token único
        raw_token = secrets.token_urlsafe(self.TOKEN_LENGTH)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Criar registro no banco
        expires_at = datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at,
        )

        db.add(reset_token)
        await db.commit()

        # Audit log: password reset request
        audit_repo = AuditRepository(db)
        await audit_repo.create_log(
            user_id=UUID(str(user.id)),
            action="password_reset_request",
            resource_type="user",
            resource_id=UUID(str(user.id)),
            extra_data={"email": user.email},
        )

        # Construir URL de reset
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

        # Enviar email
        await self.email_service.send_password_reset_email(
            to_email=user.email,
            user_name=user.full_name or user.email,
            reset_url=reset_url,
            expires_hours=self.TOKEN_EXPIRY_HOURS,
        )

        return {
            "message": "Se o email existir, você receberá instruções de recuperação",
            "success": True,
        }

    async def validate_reset_token(
        self,
        db: AsyncSession,
        raw_token: str,
    ) -> PasswordResetToken | None:
        """
        Valida token de reset.

        Args:
            db: Sessão do banco de dados
            raw_token: Token em texto plano recebido do usuário

        Returns:
            PasswordResetToken válido ou None
        """
        # Hash do token
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Buscar token
        result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token_hash)
        )
        reset_token = result.scalar_one_or_none()

        # Verificar se existe e é válido
        if not reset_token or not reset_token.is_valid:
            return None

        return reset_token

    async def confirm_password_reset(
        self,
        db: AsyncSession,
        raw_token: str,
        new_password: str,
    ) -> dict[str, str | bool]:
        """
        Confirma reset de senha.

        Valida token, atualiza senha, invalida token.

        Args:
            db: Sessão do banco de dados
            raw_token: Token em texto plano
            new_password: Nova senha

        Returns:
            Dict com sucesso/erro

        Raises:
            ValueError: Se token inválido ou expirado
        """
        # Validar token
        reset_token = await self.validate_reset_token(db, raw_token)
        if not reset_token:
            raise ValueError("Token inválido ou expirado")

        # Buscar usuário
        result = await db.execute(select(User).where(User.id == reset_token.user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Usuário não encontrado")

        # Atualizar senha
        user.password_hash = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()  # Invalidate existing JWT tokens

        # Marcar token como usado
        reset_token.used = True

        await db.commit()

        # Audit log: password changed
        audit_repo = AuditRepository(db)
        await audit_repo.create_log(
            user_id=UUID(str(user.id)),
            action="password_changed",
            resource_type="user",
            resource_id=UUID(str(user.id)),
            extra_data={"email": user.email, "method": "password_reset"},
        )

        # Enviar email de confirmação
        await self.email_service.send_password_changed_email(
            to_email=user.email,
            user_name=user.full_name or user.email,
        )

        return {
            "message": "Senha alterada com sucesso",
            "success": True,
        }

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """
        Remove tokens expirados (mais de 24h).

        Args:
            db: Sessão do banco de dados

        Returns:
            Número de tokens removidos
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.created_at < cutoff_time
            )
        )
        tokens = result.scalars().all()

        for token in tokens:
            await db.delete(token)

        await db.commit()
        return len(tokens)
