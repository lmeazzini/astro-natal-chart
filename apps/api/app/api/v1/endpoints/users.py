"""
User profile and account management endpoints.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.repositories.user_repository import OAuthAccountRepository
from app.schemas.password import PasswordChange
from app.schemas.subscription import SubscriptionRead, UserSubscriptionRead
from app.schemas.user import UserPublicProfile, UserRead, UserUpdate
from app.schemas.user_activity import UserActivityList
from app.schemas.user_stats import UserStats
from app.services import subscription_service, user_service
from app.services.amplitude_service import amplitude_service
from app.services.s3_service import s3_service

router = APIRouter()


class AvatarUploadResponse(BaseModel):
    """Response for avatar upload."""

    avatar_url: str
    message: str


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user.",
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user profile.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        User profile data
    """
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    summary="Update user profile",
    description="Update the authenticated user's profile information.",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def update_user_profile(
    request: Request,
    response: Response,
    profile_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Update user profile.

    Args:
        profile_data: Profile update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated user profile
    """
    updated_user = await user_service.update_profile(db, current_user, profile_data)

    # Track profile update
    fields_changed = list(profile_data.model_dump(exclude_unset=True).keys())
    amplitude_service.track(
        event_type="profile_updated",
        user_id=str(current_user.id),
        event_properties={
            "fields_changed": fields_changed,
            "source": "api",
        },
    )

    return updated_user


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change the authenticated user's password.",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def change_user_password(
    request: Request,
    response: Response,
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Change user password.

    Args:
        password_data: Password change data
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 400: If current password is incorrect
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        await user_service.change_password(
            db,
            current_user,
            password_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Track successful password change
        amplitude_service.track(
            event_type="profile_password_changed",
            user_id=str(current_user.id),
            event_properties={"source": "api"},
        )
    except HTTPException as e:
        # Track failed password change
        amplitude_service.track(
            event_type="profile_password_change_failed",
            user_id=str(current_user.id),
            event_properties={
                "error_type": e.detail if isinstance(e.detail, str) else "validation_error",
                "source": "api",
            },
        )
        raise


@router.get(
    "/me/stats",
    response_model=UserStats,
    summary="Get user statistics",
    description="Get statistics about the user's account (charts created, account age, etc.).",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_user_stats(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserStats:
    """
    Get user statistics.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        User statistics
    """
    return await user_service.get_stats(db, current_user)


@router.get(
    "/me/activity",
    response_model=UserActivityList,
    summary="Get user activity log",
    description="Get the activity log for the authenticated user (login history, chart operations, etc.).",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_user_activity(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> UserActivityList:
    """
    Get user activity log.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of activities to return
        offset: Number of activities to skip

    Returns:
        List of user activities
    """
    return await user_service.get_activities(db, current_user, limit=limit, offset=offset)


@router.get(
    "/me/export",
    summary="Export user data",
    description="Export all user data in JSON format (LGPD/GDPR compliance).",
)
@limiter.limit("10/hour")
async def export_user_data(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Export all user data (LGPD/GDPR compliance).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dictionary with all user data
    """
    return await user_service.export_data(db, current_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account",
    description="Soft delete the authenticated user's account. This action can be reversed within 30 days.",
)
@limiter.limit(RateLimits.CHART_DELETE)
async def delete_user_account(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Soft delete user account.

    Args:
        current_user: Authenticated user
        db: Database session
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    await user_service.soft_delete_user(
        db,
        current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get(
    "/me/oauth-connections",
    summary="Get OAuth connections",
    description="Get all OAuth provider connections for the authenticated user.",
)
async def get_oauth_connections(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """
    Get all OAuth connections for user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of OAuth connections
    """
    oauth_repo = OAuthAccountRepository(db)
    accounts = await oauth_repo.get_by_user_id(UUID(str(current_user.id)))

    return [
        {
            "provider": account.provider,
            "provider_user_id": account.provider_user_id,
            "connected_at": account.created_at.isoformat(),
        }
        for account in accounts
    ]


@router.delete(
    "/me/oauth-connections/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect OAuth provider",
    description="Disconnect an OAuth provider from the user account.",
)
async def disconnect_oauth_provider(
    provider: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Disconnect OAuth provider from user account.

    Args:
        provider: OAuth provider name (google, github, facebook)
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 400: If user has no password and this is the only OAuth connection
        HTTPException 404: If OAuth connection not found
    """
    oauth_repo = OAuthAccountRepository(db)

    # Get all user's OAuth accounts
    all_accounts = await oauth_repo.get_by_user_id(UUID(str(current_user.id)))

    # Check if user has password or other OAuth accounts
    if not current_user.password_hash and len(all_accounts) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disconnect last OAuth provider without setting a password first",
        )

    # Find the specific OAuth account to disconnect
    account_to_delete = next(
        (acc for acc in all_accounts if acc.provider == provider),
        None,
    )

    if not account_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth connection for {provider} not found",
        )

    # Delete the OAuth account
    await oauth_repo.delete(account_to_delete)

    # Track OAuth disconnection
    amplitude_service.track(
        event_type="oauth_connection_removed",
        user_id=str(current_user.id),
        event_properties={
            "provider": provider,
            "source": "api",
        },
    )


@router.post(
    "/me/avatar",
    response_model=AvatarUploadResponse,
    summary="Upload avatar image",
    description="Upload a new avatar image. Accepts JPEG, PNG, and WebP formats. Max size: 5MB.",
)
@limiter.limit(RateLimits.AVATAR_UPLOAD)
async def upload_avatar(
    request: Request,
    response: Response,
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AvatarUploadResponse:
    """
    Upload user avatar image.

    Args:
        file: Image file (JPEG, PNG, WebP)
        current_user: Authenticated user
        db: Database session

    Returns:
        Avatar URL and success message

    Raises:
        HTTPException 400: If file type is invalid or file is too large
    """
    # Validate content type
    if file.content_type not in s3_service.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(s3_service.ALLOWED_IMAGE_TYPES.keys())}",
        )

    # Read file content
    contents = await file.read()

    # Validate file size
    if len(contents) > s3_service.MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {s3_service.MAX_AVATAR_SIZE // (1024 * 1024)}MB",
        )

    try:
        # Delete old avatar if exists and is in S3
        if current_user.avatar_url and current_user.avatar_url.startswith("s3://"):
            s3_service.delete_avatar(current_user.avatar_url)

        # Upload new avatar
        s3_url = s3_service.upload_avatar(
            image_bytes=contents,
            user_id=str(current_user.id),
            content_type=file.content_type,
            filename=file.filename,
        )

        if not s3_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload avatar",
            )

        # Update user avatar_url
        current_user.avatar_url = s3_url
        await db.commit()
        await db.refresh(current_user)

        return AvatarUploadResponse(
            avatar_url=s3_url,
            message="Avatar uploaded successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/me/avatar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete avatar image",
    description="Delete the current avatar image.",
)
async def delete_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete user avatar image.

    Args:
        current_user: Authenticated user
        db: Database session
    """
    if current_user.avatar_url and current_user.avatar_url.startswith("s3://"):
        s3_service.delete_avatar(current_user.avatar_url)

    current_user.avatar_url = None
    await db.commit()


@router.get(
    "/{user_id}/profile",
    response_model=UserPublicProfile,
    summary="Get public user profile",
    description="Get the public profile of any user (if their profile is set to public).",
)
async def get_public_profile(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get public user profile.

    Args:
        user_id: UUID of the user
        db: Database session

    Returns:
        Public profile data

    Raises:
        HTTPException 404: If user not found or profile is not public
    """
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.profile_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private",
        )

    return user


@router.get(
    "/me/subscription",
    response_model=UserSubscriptionRead,
    summary="Get current user's subscription status",
    description="Get the subscription status of the currently authenticated user.",
)
async def get_my_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> UserSubscriptionRead:
    """
    Get current user's subscription status.

    Returns:
        User subscription status with details if exists
    """
    subscription = await subscription_service.get_user_subscription(
        db=db,
        user_id=UUID(str(current_user.id)),
    )

    subscription_data = None
    if subscription:
        subscription_data = SubscriptionRead.model_validate(subscription)

    return UserSubscriptionRead(
        has_subscription=subscription is not None,
        is_premium=current_user.is_premium,
        subscription=subscription_data,
    )
