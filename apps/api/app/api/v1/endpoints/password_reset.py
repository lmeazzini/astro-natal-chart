"""
Password reset endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.services.password_reset import PasswordResetService

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperação de senha",
    description="""
    Solicita recuperação de senha enviando email com link de reset.

    **Nota de segurança**: Sempre retorna sucesso mesmo se o email não existir
    para não revelar informações sobre usuários cadastrados.

    **Rate limit**: 3 requisições por minuto por IP.
    """,
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """
    Solicita recuperação de senha.

    Envia email com link de recuperação se o email existir no sistema.
    """
    service = PasswordResetService()
    result = await service.request_password_reset(db, request.email)

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

    **Rate limit**: 5 requisições por minuto por IP.
    """,
)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> PasswordResetResponse:
    """
    Confirma reset de senha com token.

    Valida token, atualiza senha do usuário.
    """
    service = PasswordResetService()

    try:
        result = await service.confirm_password_reset(
            db, request.token, request.new_password
        )

        return PasswordResetResponse(
            message=result["message"],
            success=result["success"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
