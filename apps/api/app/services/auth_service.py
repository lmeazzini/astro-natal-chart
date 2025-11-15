"""
Authentication service for user registration, login, and token management.
"""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import OAuthAccount, User
from app.repositories.user_repository import OAuthAccountRepository, UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""

    pass


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Register a new user with email and password.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created user instance

    Raises:
        UserAlreadyExistsError: If email already registered
    """
    user_repo = UserRepository(db)

    # Check if user already exists
    if await user_repo.email_exists(user_data.email):
        raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

    # Create new user
    user = User(
        id=uuid4(),
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        locale=settings.DEFAULT_LOCALE,
        timezone=settings.DEFAULT_TIMEZONE,
        email_verified=False,
        is_active=True,
        is_superuser=False,
    )

    return await user_repo.create(user)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Authenticate user with email and password.

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        Authenticated user instance

    Raises:
        AuthenticationError: If credentials are invalid
    """
    user_repo = UserRepository(db)

    # Find user by email
    user = await user_repo.get_by_email(email)

    if not user:
        raise AuthenticationError("Invalid email or password")

    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    # Check if user is active
    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    return user


async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    """
    Login user and generate access and refresh tokens.

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        Token object with access and refresh tokens

    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Authenticate user
    user = await authenticate_user(db, email, password)

    # Generate tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_access_token(db: AsyncSession, user_id: UUID) -> Token:
    """
    Generate new access token from refresh token.

    Args:
        db: Database session
        user_id: User ID from refresh token

    Returns:
        Token object with new access token

    Raises:
        AuthenticationError: If user not found or inactive
    """
    user_repo = UserRepository(db)

    # Find active user
    user = await user_repo.get_active_user_by_id(user_id)

    if not user:
        raise AuthenticationError("User not found or inactive")

    # Generate new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


async def create_or_update_oauth_user(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: str,
    full_name: str,
    avatar_url: str | None = None,
) -> tuple[User, bool]:
    """
    Create or update user from OAuth provider.

    Args:
        db: Database session
        provider: OAuth provider (google, github, facebook)
        provider_user_id: User ID from provider
        email: User email
        full_name: User full name
        avatar_url: User avatar URL

    Returns:
        Tuple of (user, is_new) where is_new indicates if user was created

    Raises:
        AuthenticationError: If OAuth account exists for different user
    """
    user_repo = UserRepository(db)
    oauth_repo = OAuthAccountRepository(db)

    # Check if OAuth account exists
    oauth_account = await oauth_repo.get_by_provider_and_user_id(provider, provider_user_id)

    if oauth_account:
        # Update existing OAuth account
        user = oauth_account.user
        user.avatar_url = avatar_url or user.avatar_url
        await user_repo.update(user)
        return user, False

    # Check if user with email exists
    existing_user = await user_repo.get_by_email(email)

    if existing_user is not None:
        # Link OAuth account to existing user
        oauth_account = OAuthAccount(
            id=uuid4(),
            user_id=existing_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
        await oauth_repo.create(oauth_account)

        existing_user.email_verified = True  # Verified by OAuth provider
        existing_user.avatar_url = avatar_url or existing_user.avatar_url
        await user_repo.update(existing_user)
        return existing_user, False

    # Create new user with OAuth account
    user = User(
        id=uuid4(),
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
        locale=settings.DEFAULT_LOCALE,
        timezone=settings.DEFAULT_TIMEZONE,
        email_verified=True,  # Verified by OAuth provider
        is_active=True,
        is_superuser=False,
    )
    await user_repo.create(user)

    # Create OAuth account
    oauth_account = OAuthAccount(
        id=uuid4(),
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
    )
    await oauth_repo.create(oauth_account)

    return user, True


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User instance or None if not found
    """
    user_repo = UserRepository(db)
    return await user_repo.get_by_id(user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Get user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User instance or None if not found
    """
    user_repo = UserRepository(db)
    return await user_repo.get_by_email(email)
