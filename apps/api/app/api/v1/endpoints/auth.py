"""
Authentication endpoints for user registration, login, and token management.
"""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token, TokenVerify
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with email and password. Password must meet strength requirements.",
)
@limiter.limit(RateLimits.REGISTER)
async def register(
    request: Request,
    response: Response,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data (email, password, full_name)
        db: Database session

    Returns:
        Created user data

    Raises:
        HTTPException 400: If user already exists or validation fails
    """
    try:
        # Extract IP address and user agent for consent tracking
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        user = await auth_service.register_user(
            db,
            user_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return user
    except auth_service.UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user with email and password, returns JWT tokens.",
)
@limiter.limit(RateLimits.LOGIN)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Login user with email and password.

    Args:
        login_data: Login credentials (email, password)
        db: Database session

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        token = await auth_service.login_user(
            db,
            email=login_data.email,
            password=login_data.password,
        )
        return token
    except auth_service.AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Generate new access token using refresh token.",
)
@limiter.limit(RateLimits.REFRESH)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        New JWT access token

    Raises:
        HTTPException 401: If refresh token is invalid
    """
    try:
        # Decode and validate refresh token
        payload = decode_token(refresh_data.refresh_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token type is refresh
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user_id from token
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        from uuid import UUID

        user_id = UUID(user_id_str)

        # Generate new access token
        token = await auth_service.refresh_access_token(db, user_id)
        return token

    except auth_service.AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
    description="Get current authenticated user information.",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current authenticated user.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        Current user data
    """
    return current_user


@router.get(
    "/verify",
    response_model=TokenVerify,
    summary="Verify access token",
    description="Verify if current access token is valid and get expiration info.",
)
@limiter.limit(RateLimits.REFRESH)
async def verify_token(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
) -> TokenVerify:
    """
    Verify if current access token is valid.

    Returns token expiration time and user info. This endpoint is useful
    for the frontend to check token validity and decide when to refresh.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user from JWT token

    Returns:
        Token verification info including expiration time
    """
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    # Decode token to get expiration
    payload = decode_token(token)
    exp = payload.get("exp", 0) if payload else 0
    expires_in = max(0, int(exp - time.time()))

    return TokenVerify(
        valid=True,
        user_id=str(current_user.id),
        email=current_user.email,
        expires_in=expires_in,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Logout current user (client should discard tokens).",
)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Logout user.

    Note: With JWT tokens, logout is handled client-side by discarding tokens.
    This endpoint exists for consistency and future token blacklisting.

    Args:
        current_user: Current authenticated user from JWT token
    """
    # With JWT, logout is handled client-side
    # In the future, we could implement token blacklisting here
    pass


@router.get(
    "/verify-email/{token}",
    response_model=UserRead,
    summary="Verify email",
    description="Verify user email address using verification token from email.",
)
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Verify user email address.

    Args:
        token: Email verification JWT token from email link
        db: Database session

    Returns:
        Verified user data

    Raises:
        HTTPException 400: If token is invalid or expired
    """
    try:
        user = await auth_service.verify_email(db, token)
        return user
    except auth_service.AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend email verification to current user.",
)
@limiter.limit(RateLimits.REGISTER)  # Same rate limit as registration
async def resend_verification_email(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Resend verification email to current user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If email already verified or sending fails
    """
    try:
        await auth_service.resend_verification_email(db, current_user)
        return {"message": "Verification email sent successfully"}
    except auth_service.AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
