"""
Security utilities: password hashing, JWT creation/validation.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional expiration time, defaults to ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return cast(str, encoded_jwt)


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return cast(str, encoded_jwt)


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return cast(dict[str, Any], payload) if payload else None
    except JWTError:
        return None


def create_email_verification_token(email: str, user_id: str) -> str:
    """
    Create a JWT token for email verification (24h expiry).

    Args:
        email: User email address
        user_id: User ID (UUID as string)

    Returns:
        Encoded JWT token for email verification
    """
    data = {
        "sub": user_id,
        "email": email,
        "type": "email_verification",
    }
    expires_delta = timedelta(hours=24)
    return create_access_token(data, expires_delta)


def verify_email_verification_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode an email verification token.

    Args:
        token: JWT verification token

    Returns:
        Decoded payload with user_id and email, or None if invalid/expired
    """
    payload = decode_token(token)

    if not payload:
        return None

    # Verify it's an email verification token
    if payload.get("type") != "email_verification":
        return None

    # Check required fields
    if "sub" not in payload or "email" not in payload:
        return None

    return payload
