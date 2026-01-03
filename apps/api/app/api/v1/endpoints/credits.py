"""Credit system API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credit_config import FEATURE_CREDIT_COSTS, PLAN_CREDIT_LIMITS
from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.credit import (
    AddBonusCreditsRequest,
    CreditCostInfo,
    CreditHistoryResponse,
    CreditsInfoResponse,
    CreditTransactionRead,
    CreditUsageResponse,
    UnlockedFeaturesResponse,
    UpgradePlanRequest,
    UserCreditResponse,
)
from app.services import credit_service
from app.services.chart_service import ChartNotFoundError, ChartService, get_chart_service

router = APIRouter(prefix="/credits")


@router.get(
    "",
    response_model=UserCreditResponse,
    summary="Get current credit balance",
    description="Get the current user's credit balance and plan information.",
)
async def get_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserCreditResponse:
    """Get current user's credit balance."""
    user_credit = await credit_service.get_or_create_user_credits(
        db=db,
        user_id=current_user.id,
    )

    return UserCreditResponse(
        plan_type=user_credit.plan_type,
        credits_balance=user_credit.credits_balance,
        credits_limit=user_credit.credits_limit,
        credits_used=user_credit.credits_used,
        usage_percentage=user_credit.usage_percentage,
        is_unlimited=user_credit.is_unlimited,
        period_start=user_credit.period_start,
        period_end=user_credit.period_end,
        days_until_reset=user_credit.days_until_reset,
    )


@router.get(
    "/history",
    response_model=CreditHistoryResponse,
    summary="Get credit transaction history",
    description="Get paginated history of credit transactions for the current user.",
)
async def get_credit_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreditHistoryResponse:
    """Get credit transaction history."""
    transactions, total = await credit_service.get_credit_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return CreditHistoryResponse(
        transactions=[CreditTransactionRead.model_validate(t) for t in transactions],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/usage",
    response_model=CreditUsageResponse,
    summary="Get credit usage breakdown",
    description="Get breakdown of credits consumed per feature type in current period.",
)
async def get_credit_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreditUsageResponse:
    """Get credit usage breakdown by feature."""
    user_credit = await credit_service.get_or_create_user_credits(
        db=db,
        user_id=current_user.id,
    )

    usage_by_feature = await credit_service.get_usage_breakdown(
        db=db,
        user_id=current_user.id,
    )

    total_used = sum(usage_by_feature.values())

    return CreditUsageResponse(
        usage_by_feature=usage_by_feature,
        total_used=total_used,
        period_start=user_credit.period_start,
        period_end=user_credit.period_end,
    )


@router.get(
    "/info",
    response_model=CreditsInfoResponse,
    summary="Get credit cost information",
    description="Get public information about credit costs and plan limits.",
)
async def get_credits_info() -> CreditsInfoResponse:
    """Get public credit cost information."""
    feature_costs = [
        CreditCostInfo(feature_type=k, cost=v) for k, v in FEATURE_CREDIT_COSTS.items()
    ]

    return CreditsInfoResponse(
        plans=PLAN_CREDIT_LIMITS,
        feature_costs=feature_costs,
    )


@router.get(
    "/charts/{chart_id}/unlocked-features",
    response_model=UnlockedFeaturesResponse,
    summary="Get unlocked features for a chart",
    description="""
Get the list of premium features that have been unlocked (paid) for a specific chart.

This endpoint returns:
- **unlocked_features**: List of feature types (longevity, saturn_return, growth, solar_return)
  that have been unlocked for this chart
- **unlocked_solar_return_years**: List of years for which Solar Return has been unlocked
  (Solar Return is charged per year)

Use this to determine whether to show the premium feature card or load the data directly.
""",
    responses={
        404: {"description": "Chart not found or not owned by user"},
    },
)
async def get_unlocked_features(
    chart_id: UUID,
    current_user: User = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
    db: AsyncSession = Depends(get_db),
) -> UnlockedFeaturesResponse:
    """Get unlocked features for a specific chart."""
    # Verify chart ownership
    try:
        await chart_service.get_chart_by_id(chart_id, current_user.id)
    except ChartNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        ) from err

    # Get unlocked features
    result = await credit_service.get_unlocked_features_for_chart(
        db=db,
        user_id=current_user.id,
        chart_id=chart_id,
    )

    return UnlockedFeaturesResponse(
        unlocked_features=result["unlocked_features"],
        unlocked_solar_return_years=result["unlocked_solar_return_years"],
    )


# Admin endpoints
admin_router = APIRouter(prefix="/admin/credits")


@admin_router.post(
    "/users/{user_id}/bonus",
    response_model=CreditTransactionRead,
    summary="Add bonus credits to user",
    description="Admin: Add bonus credits to a user's account.",
)
async def add_bonus_credits(
    user_id: UUID,
    request: AddBonusCreditsRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CreditTransactionRead:
    """Add bonus credits to a user."""
    transaction = await credit_service.add_bonus_credits(
        db=db,
        user_id=user_id,
        amount=request.amount,
        admin_user=admin_user,
        reason=request.reason,
    )

    return CreditTransactionRead.model_validate(transaction)


@admin_router.post(
    "/users/{user_id}/plan",
    response_model=UserCreditResponse,
    summary="Change user's plan",
    description="Admin: Change a user's plan type and allocate credits accordingly.",
)
async def change_user_plan(
    user_id: UUID,
    request: UpgradePlanRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserCreditResponse:
    """Change a user's plan type."""
    user_credit = await credit_service.allocate_credits(
        db=db,
        user_id=user_id,
        plan_type=request.plan_type,
        changed_by_admin_id=admin_user.id,
    )

    return UserCreditResponse(
        plan_type=user_credit.plan_type,
        credits_balance=user_credit.credits_balance,
        credits_limit=user_credit.credits_limit,
        credits_used=user_credit.credits_used,
        usage_percentage=user_credit.usage_percentage,
        is_unlimited=user_credit.is_unlimited,
        period_start=user_credit.period_start,
        period_end=user_credit.period_end,
        days_until_reset=user_credit.days_until_reset,
    )


@admin_router.get(
    "/users/{user_id}",
    response_model=UserCreditResponse,
    summary="Get user's credits",
    description="Admin: Get a specific user's credit information.",
)
async def get_user_credits(
    user_id: UUID,
    _admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserCreditResponse:
    """Get a specific user's credit information."""
    user_credit = await credit_service.get_or_create_user_credits(
        db=db,
        user_id=user_id,
    )

    return UserCreditResponse(
        plan_type=user_credit.plan_type,
        credits_balance=user_credit.credits_balance,
        credits_limit=user_credit.credits_limit,
        credits_used=user_credit.credits_used,
        usage_percentage=user_credit.usage_percentage,
        is_unlimited=user_credit.is_unlimited,
        period_start=user_credit.period_start,
        period_end=user_credit.period_end,
        days_until_reset=user_credit.days_until_reset,
    )


@admin_router.get(
    "/users/{user_id}/history",
    response_model=CreditHistoryResponse,
    summary="Get user's credit history",
    description="Admin: Get credit transaction history for a specific user.",
)
async def get_user_credit_history(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    _admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CreditHistoryResponse:
    """Get credit transaction history for a specific user."""
    transactions, total = await credit_service.get_credit_history(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return CreditHistoryResponse(
        transactions=[CreditTransactionRead.model_validate(t) for t in transactions],
        total=total,
        skip=skip,
        limit=limit,
    )
