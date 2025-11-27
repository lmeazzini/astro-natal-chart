"""
Password reset endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import RateLimits, limiter
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.services.password_reset import PasswordResetService
from app.services.amplitude_service import amplitude_service

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


@router.post(
    "/request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperação de senha",
    description="""
    Solicita recuperação de senha enviando email com link de reset.

    **Nota de segurança**: Sempre retorna sucesso mesmo se o email não existir
    para não revelar informações sobre usuários cadastrados.

    **Rate limit**: 3 requisições por hora por IP.
    """,
)
@limiter.limit(RateLimits.PASSWORD_RESET_REQUEST)
async def request_password_reset(
    http_request: Request,
    http_response: Response,
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """
    Solicita recuperação de senha.

    Envia email com link de recuperação se o email existir no sistema.
    """
    service = PasswordResetService()
    result = await service.request_password_reset(db, request.email)

    # Track password reset request (success or not)
    if result["success"]:
        amplitude_service.track(
            event_type="password_reset_email_sent",
            event_properties={
                "method": "email_request",
            },
        )
    else:
        amplitude_service.track(
            event_type="password_reset_failed",
            event_properties={
                "error_type": "request_failed",
            },
        )

    return PasswordResetResponse(
        message=result["message"],
        success=result["success"],
    )


@router.post(
    "/confirm",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirmar recuperação de senha",
    description="""
    Confirma recuperação de senha usando token recebido por email.

    Valida o token, atualiza a senha e invalida o token.

    **Rate limit**: 5 requisições por hora por IP.
    """,
)
@limiter.limit(RateLimits.PASSWORD_RESET_CONFIRM)
async def confirm_password_reset(
    http_request: Request,
    http_response: Response,
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """
    Confirma reset de senha com token.

    Valida token, atualiza senha do usuário.
    """
    service = PasswordResetService()

    try:
        result = await service.confirm_password_reset(db, request.token, request.new_password)

        # Track successful password reset
        if result["success"]:
            # Note: We don't have user_id here as the service returns success/message
            # The user_id would need to be added to the service response to track with user context
            amplitude_service.track(
                event_type="password_reset_completed",
                event_properties={
                    "method": "email_link",
                },
            )

        return PasswordResetResponse(
            message=result["message"],
            success=result["success"],
        )
    except ValueError as e:
        # Track password reset failure
        amplitude_service.track(
            event_type="password_reset_failed",
            event_properties={
                "error_type": "invalid_token_or_password",
            },
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
