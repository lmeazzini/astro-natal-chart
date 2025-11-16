"""
Privacy and LGPD compliance Celery tasks.
"""

import asyncio
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import delete, select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.chart import AuditLog, BirthChart
from app.models.password_reset import PasswordResetToken
from app.models.user import OAuthAccount, User
from app.models.user_consent import UserConsent


@celery_app.task(name="privacy.cleanup_deleted_users")
def cleanup_deleted_users() -> dict[str, int]:
    """
    Hard delete de usuários marcados para exclusão há mais de 30 dias.

    **LGPD Compliance**: Direito ao esquecimento (Art. 18, VI).

    **Processo**:
    1. Encontra usuários com deleted_at > 30 dias atrás
    2. Remove TODOS os dados relacionados:
       - Mapas natais
       - Consentimentos
       - Tokens de reset
       - Contas OAuth
       - Usuário
    3. Mantém audit logs (5 anos - obrigação legal)

    **Agendamento**: Executar diariamente às 3h (horário de baixo tráfego).

    Returns:
        Dict com estatísticas de exclusão
    """
    return asyncio.run(_cleanup_deleted_users_async())


async def _cleanup_deleted_users_async() -> dict[str, int]:
    """Versão async da tarefa de hard delete."""
    async with AsyncSessionLocal() as db:
        # Data de corte: 30 dias atrás
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Encontrar usuários para hard delete
        result = await db.execute(
            select(User).where(
                User.deleted_at.isnot(None),
                User.deleted_at < cutoff_date,
            )
        )
        users_to_delete = result.scalars().all()

        stats = {
            "users_deleted": 0,
            "birth_charts_deleted": 0,
            "oauth_accounts_deleted": 0,
            "consents_deleted": 0,
            "password_reset_tokens_deleted": 0,
        }

        for user in users_to_delete:
            logger.info(f"Hard deleting user {user.id} (email: {user.email})")

            # Registrar audit log ANTES de deletar
            audit_log = AuditLog(
                user_id=user.id,
                action="account_hard_deleted",
                resource_type="user",
                resource_id=user.id,
                ip_address=None,
                details={
                    "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
                    "hard_deleted_at": datetime.utcnow().isoformat(),
                    "retention_period_days": 30,
                },
            )
            db.add(audit_log)

            # 1. Deletar mapas natais
            charts_result = await db.execute(
                delete(BirthChart).where(BirthChart.user_id == user.id)
            )
            stats["birth_charts_deleted"] += charts_result.rowcount or 0

            # 2. Deletar contas OAuth
            oauth_result = await db.execute(
                delete(OAuthAccount).where(OAuthAccount.user_id == user.id)
            )
            stats["oauth_accounts_deleted"] += oauth_result.rowcount or 0

            # 3. Deletar consentimentos
            consents_result = await db.execute(
                delete(UserConsent).where(UserConsent.user_id == user.id)
            )
            stats["consents_deleted"] += consents_result.rowcount or 0

            # 4. Deletar tokens de reset
            tokens_result = await db.execute(
                delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
            )
            stats["password_reset_tokens_deleted"] += tokens_result.rowcount or 0

            # 5. Deletar usuário
            await db.delete(user)
            stats["users_deleted"] += 1

            logger.info(f"Successfully hard deleted user {user.id}")

        # Commit todas as exclusões
        await db.commit()

        logger.info(f"Hard delete completed: {stats}")
        return stats
