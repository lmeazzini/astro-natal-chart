"""
Authentication schemas for login, tokens, OAuth2.
"""

from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""

    user_id: str | None = None
    email: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class TokenVerify(BaseModel):
    """Schema for token verification response."""

    valid: bool = Field(..., description="Whether the token is valid")
    user_id: str = Field(..., description="User ID from token")
    email: str = Field(..., description="User email")
    expires_in: int = Field(..., description="Seconds until token expiration")

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "expires_in": 850,
            }
        }


class OAuthCallbackRequest(BaseModel):
    """Schema for OAuth2 callback."""

    code: str
    state: str | None = None


class PasswordResetRequest(BaseModel):
    """Request para iniciar recuperação de senha."""

    email: EmailStr = Field(..., description="Email do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
            }
        }


class PasswordResetConfirm(BaseModel):
    """Request para confirmar recuperação de senha com token."""

    token: str = Field(
        ...,
        min_length=32,
        max_length=128,
        description="Token de recuperação recebido por email",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Nova senha (mínimo 8 caracteres)",
    )
    password_confirm: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Confirmação da nova senha",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida força da senha."""
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info: Any) -> str:
        """Valida que as senhas coincidem."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("As senhas não coincidem")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "a1b2c3d4e5f6...",
                "new_password": "NewSecurePassword123!",
                "password_confirm": "NewSecurePassword123!",
            }
        }


class PasswordResetResponse(BaseModel):
    """Response genérico para operações de password reset."""

    message: str = Field(..., description="Mensagem de confirmação")
    success: bool = Field(default=True, description="Se operação foi bem-sucedida")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Email de recuperação enviado com sucesso",
                "success": True,
            }
        }
