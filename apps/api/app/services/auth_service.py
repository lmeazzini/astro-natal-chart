"""
Authentication service for user registration, login, and token management.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    get_password_hash,
    verify_password,
)
from app.models.user import OAuthAccount, User
from app.models.user_consent import UserConsent
from app.repositories.user_repository import OAuthAccountRepository, UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""

    pass


async def register_user(
    db: AsyncSession,
    user_data: UserCreate,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> User:
    """
    Register a new user with email and password.

    Args:
        db: Database session
        user_data: User registration data
        ip_address: User's IP address for consent tracking
        user_agent: User's browser User-Agent for consent tracking

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

    created_user = await user_repo.create(user)

    # Send verification email
    from app.services.email import EmailService

    # Generate verification token
    token = create_email_verification_token(created_user.email, str(created_user.id))
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"

    # Send email (don't fail registration if email fails)
    try:
        email_service = EmailService()
        await email_service.send_verification_email(
            to_email=created_user.email,
            user_name=created_user.full_name,
            verification_url=verification_url,
        )
    except Exception:
        # Log but don't fail registration
        pass

    # If user accepted terms, create consent record
    if user_data.accept_terms:
        # Terms of Service consent
        terms_text = (
            "Ao criar uma conta, você concorda com nossos Termos de Uso, "
            "incluindo a coleta e processamento de seus dados pessoais conforme "
            "descrito em nossa Política de Privacidade."
        )
        consent = UserConsent(
            id=uuid4(),
            user_id=created_user.id,
            consent_type="terms",
            version="1.0",
            accepted=True,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=terms_text,
        )
        db.add(consent)

        # Privacy Policy consent
        privacy_text = (
            "Você aceita nossa Política de Privacidade, incluindo o uso de cookies "
            "essenciais para o funcionamento do site e a proteção de seus dados "
            "conforme a LGPD e GDPR."
        )
        privacy_consent = UserConsent(
            id=uuid4(),
            user_id=created_user.id,
            consent_type="privacy",
            version="1.0",
            accepted=True,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=privacy_text,
        )
        db.add(privacy_consent)
        await db.commit()

    return created_user


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

    # Update last login and activity timestamps
    user.last_login_at = datetime.now(UTC)
    user.last_activity_at = datetime.now(UTC)

    user_repo = UserRepository(db)
    await user_repo.update(user)

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


async def verify_email(db: AsyncSession, token: str) -> User:
    """
    Verify user email using verification token.

    Args:
        db: Database session
        token: Email verification JWT token

    Returns:
        Verified user instance

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    from app.core.security import verify_email_verification_token

    # Decode and validate token
    payload = verify_email_verification_token(token)

    if not payload:
        raise AuthenticationError("Invalid or expired verification token")

    # Extract user_id from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid token payload")

    user_id = UUID(user_id_str)
    user_repo = UserRepository(db)

    # Get user
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found")

    # Check if already verified
    if user.email_verified:
        return user  # Already verified, no error

    # Verify email
    user.email_verified = True
    await user_repo.update(user)

    # Send welcome email after successful verification
    from app.services.email import EmailService

    email_service = EmailService()
    try:
        await email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.full_name or "Usuário",
        )
    except Exception as e:
        # Log error but don't fail verification if email fails
        logger.error(
            f"Failed to send welcome email after verification: {e}",
            extra={"user_id": str(user.id), "email": user.email}
        )

    return user


async def resend_verification_email(db: AsyncSession, user: User) -> None:
    """
    Resend email verification to user.

    Args:
        db: Database session
        user: User instance

    Raises:
        AuthenticationError: If email already verified or sending fails
    """
    from app.core.config import settings
    from app.core.security import create_email_verification_token
    from app.services.email import EmailService

    # Check if already verified
    if user.email_verified:
        raise AuthenticationError("Email already verified")

    # Generate new verification token
    token = create_email_verification_token(user.email, str(user.id))

    # Build verification URL
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"

    # Send verification email
    email_service = EmailService()
    success = await email_service.send_verification_email(
        to_email=user.email,
        user_name=user.full_name,
        verification_url=verification_url,
    )

    if not success:
        raise AuthenticationError("Failed to send verification email")
