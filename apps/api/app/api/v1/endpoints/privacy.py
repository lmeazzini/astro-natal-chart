"""
Privacy and LGPD/GDPR compliance endpoints.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.chart import AuditLog, BirthChart
from app.models.user import OAuthAccount, User
from app.models.user_consent import UserConsent
from app.services.amplitude_service import amplitude_service

router = APIRouter(prefix="/users/me", tags=["Privacy & LGPD"])


@router.get(
    "/export",
    summary="Exportar todos os dados do usuário (LGPD Art. 18, V)",
    description="""
    Exporta todos os dados pessoais do usuário em formato JSON estruturado.

    **Direito à portabilidade** (LGPD Art. 18, V):
    - Dados de cadastro (nome, email, idioma, fuso)
    - Mapas natais criados
    - Consentimentos aceitos
    - Histórico de ações (audit logs)
    - Contas OAuth vinculadas

    **Formato**: JSON estruturado e legível por máquina.
    **Prazo**: Resposta imediata (processamento síncrono).
    """,
)
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Exporta todos os dados do usuário (data portability).

    Conforme LGPD Art. 18, V - Direito à portabilidade.
    """
    # 1. Dados básicos do usuário
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "locale": current_user.locale,
        "timezone": current_user.timezone,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "deleted_at": current_user.deleted_at.isoformat() if current_user.deleted_at else None,
    }

    # 2. Contas OAuth vinculadas
    oauth_result = await db.execute(
        select(OAuthAccount).where(OAuthAccount.user_id == current_user.id)
    )
    oauth_accounts = oauth_result.scalars().all()
    oauth_data = [
        {
            "provider": account.provider,
            "provider_user_id": account.provider_user_id,
            "created_at": account.created_at.isoformat() if account.created_at else None,
        }
        for account in oauth_accounts
    ]

    # 3. Mapas natais
    charts_result = await db.execute(
        select(BirthChart).where(
            BirthChart.user_id == current_user.id,
            BirthChart.deleted_at.is_(None),
        )
    )
    charts = charts_result.scalars().all()
    charts_data = [
        {
            "id": str(chart.id),
            "person_name": chart.person_name,
            "birth_datetime": chart.birth_datetime.isoformat() if chart.birth_datetime else None,
            "birth_timezone": chart.birth_timezone,
            "latitude": float(chart.latitude),
            "longitude": float(chart.longitude),
            "city": chart.city,
            "country": chart.country,
            "chart_data": chart.chart_data,  # Full calculation data
            "created_at": chart.created_at.isoformat() if chart.created_at else None,
            "updated_at": chart.updated_at.isoformat() if chart.updated_at else None,
        }
        for chart in charts
    ]

    # 4. Consentimentos
    consents_result = await db.execute(
        select(UserConsent).where(UserConsent.user_id == current_user.id)
    )
    consents = consents_result.scalars().all()
    consents_data = [
        {
            "consent_type": consent.consent_type,
            "version": consent.version,
            "accepted": consent.accepted,
            "created_at": consent.created_at.isoformat() if consent.created_at else None,
            "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
            "ip_address": consent.ip_address,
        }
        for consent in consents
    ]

    # 5. Audit logs (últimos 90 dias apenas - para não expor demais)
    from datetime import timedelta

    cutoff_date = datetime.now(UTC) - timedelta(days=90)

    audit_result = await db.execute(
        select(AuditLog)
        .where(
            AuditLog.user_id == current_user.id,
            AuditLog.created_at >= cutoff_date,
        )
        .order_by(AuditLog.created_at.desc())
    )
    audit_logs = audit_result.scalars().all()
    audit_data = [
        {
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "ip_address": log.ip_address,
        }
        for log in audit_logs
    ]

    # Montar JSON final
    export_data = {
        "export_info": {
            "requested_at": datetime.now(UTC).isoformat(),
            "format": "JSON",
            "compliance": "LGPD Art. 18, V - Direito à portabilidade de dados",
        },
        "user": user_data,
        "oauth_accounts": oauth_data,
        "birth_charts": charts_data,
        "consents": consents_data,
        "audit_logs_last_90_days": audit_data,
        "statistics": {
            "total_charts": len(charts_data),
            "total_consents": len(consents_data),
            "total_oauth_accounts": len(oauth_data),
        },
    }

    return export_data


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Solicitar exclusão de conta (LGPD Art. 18, VI)",
    description="""
    Solicita a exclusão da conta do usuário (soft delete).

    **Direito ao esquecimento** (LGPD Art. 18, VI):
    - Soft delete: Conta marcada como deletada (30 dias de carência)
    - Durante 30 dias: Você pode cancelar a exclusão fazendo login
    - Após 30 dias: Hard delete automático via Celery task
    - Hard delete: Dados são **permanentemente apagados** do banco

    **Dados excluídos:**
    - Perfil do usuário
    - Todos os mapas natais
    - Consentimentos
    - Tokens de reset de senha
    - Contas OAuth vinculadas

    **Dados retidos (obrigação legal):**
    - Audit logs (5 anos - Art. 16 LGPD)

    **Importante**: Esta ação é **irreversível** após 30 dias.
    """,
)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Soft delete da conta do usuário.

    Conforme LGPD Art. 18, VI - Direito ao esquecimento.
    """
    # Verificar se já está em processo de exclusão
    if current_user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conta já solicitada para exclusão em {current_user.deleted_at.isoformat()}. "
            f"Será permanentemente excluída após 30 dias. "
            f"Para cancelar, faça login novamente.",
        )

    # Marcar para soft delete
    current_user.deleted_at = datetime.now(UTC)

    # Audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="account_deletion_requested",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=None,  # TODO: Get from request
        details={"reason": "user_request"},
    )
    db.add(audit_log)

    await db.commit()

    # Track account deletion request
    amplitude_service.track(
        event_type="account_deletion_requested",
        user_id=str(current_user.id),
        event_properties={
            "deletion_type": "scheduled",
            "scheduled_days": 30,
            "source": "api",
        },
    )

    return {
        "message": "Solicitação de exclusão registrada com sucesso",
        "deleted_at": current_user.deleted_at.isoformat(),
        "permanent_deletion_date": (current_user.deleted_at + timedelta(days=30)).isoformat(),
        "cancellation_instructions": "Para cancelar a exclusão, faça login novamente nos próximos 30 dias",
    }


@router.post(
    "/cancel-deletion",
    summary="Cancelar solicitação de exclusão de conta",
    description="""
    Cancela uma solicitação anterior de exclusão de conta.

    **Disponível apenas durante o período de carência (30 dias).**

    Após cancelamento, a conta volta ao estado normal.
    """,
)
async def cancel_account_deletion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Cancela soft delete da conta."""
    if not current_user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma solicitação de exclusão ativa para esta conta",
        )

    # Verificar se ainda está no período de carência (30 dias)
    from datetime import timedelta

    if datetime.now(UTC) > (current_user.deleted_at + timedelta(days=30)):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Período de carência expirado. Conta será excluída em breve.",
        )

    # Restaurar conta
    deleted_at = current_user.deleted_at
    days_remaining = 30 - (datetime.now(UTC) - deleted_at).days if deleted_at else 0
    current_user.deleted_at = None

    # Audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="account_deletion_cancelled",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=None,  # TODO: Get from request
        details={"original_deletion_date": deleted_at.isoformat() if deleted_at else None},
    )
    db.add(audit_log)

    await db.commit()

    # Track account deletion cancellation
    amplitude_service.track(
        event_type="account_deletion_cancelled",
        user_id=str(current_user.id),
        event_properties={
            "days_remaining": days_remaining,
            "source": "api",
        },
    )

    return {
        "message": "Solicitação de exclusão cancelada com sucesso",
        "status": "active",
    }
