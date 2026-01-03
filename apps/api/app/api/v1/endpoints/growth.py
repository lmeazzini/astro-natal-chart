"""
Personal growth suggestions endpoints.

Provides AI-powered personal development suggestions based on natal chart analysis.

CREDIT FEATURE: This endpoint consumes 2 credits per generation.
Results are cached in chart_data to avoid re-consumption.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credit_config import get_feature_cost
from app.core.dependencies import get_current_user, get_db
from app.core.i18n import normalize_locale
from app.core.rate_limit import RateLimits, limiter
from app.models.enums import FeatureType
from app.models.user import User
from app.schemas.growth import (
    GrowthSuggestionsRequest,
    GrowthSuggestionsResponse,
)
from app.services import chart_service, credit_service
from app.services.personal_growth_service import PersonalGrowthService
from app.utils.chart_data_accessor import extract_language_data

router = APIRouter()


@router.post(
    "/charts/{chart_id}/growth-suggestions",
    response_model=GrowthSuggestionsResponse,
    summary="Generate personal growth suggestions",
    description=(
        "Generate AI-powered personal development suggestions based on the natal chart. "
        "Includes growth points, challenges, opportunities, and life purpose insights. "
        "\n\n**Credit Cost**: 2 credits (first generation only)."
        "\nIf you have already paid for this feature on this chart, no credits will be charged."
    ),
    responses={
        402: {"description": "Insufficient credits"},
        403: {
            "description": "Unauthorized access",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this chart"},
                }
            },
        },
        404: {
            "description": "Chart not found",
            "content": {"application/json": {"example": {"detail": "Chart not found"}}},
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded: 10 per 1 hour"}}
            },
        },
    },
)
@limiter.limit(RateLimits.GROWTH_SUGGESTIONS)
async def generate_growth_suggestions(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: GrowthSuggestionsRequest | None = None,
) -> GrowthSuggestionsResponse:
    """
    Generate personalized growth suggestions based on natal chart.

    This endpoint analyzes the natal chart and generates:
    - Growth Points: Areas that need development with actionable steps
    - Challenges: Obstacles to overcome with strategies
    - Opportunities: Natural talents to leverage
    - Purpose: Life direction and vocation insights

    Args:
        request: FastAPI request object (for rate limiting)
        chart_id: Chart UUID
        current_user: Current authenticated user with sufficient credits
        db: Database session
        body: Optional request body with focus areas

    Returns:
        GrowthSuggestionsResponse with all suggestion categories

    Raises:
        HTTPException: If chart not found, unauthorized, or processing error
    """
    try:
        # Get user's preferred language
        user_language = normalize_locale(current_user.locale) or "pt-BR"
        locale = user_language.replace("_", "-")

        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Check for cached growth suggestions in chart_data
        chart_data = extract_language_data(chart.chart_data, locale)
        if chart_data:
            cached_growth = chart_data.get("growth_suggestions")
            if cached_growth:
                logger.info(
                    "Returning cached growth suggestions for chart {} (user: {})",
                    chart_id,
                    current_user.email,
                )
                return GrowthSuggestionsResponse(**cached_growth)

        # Check if feature is already unlocked (previously paid)
        feature_unlocked = await credit_service.has_feature_unlocked(
            db=db,
            user_id=current_user.id,
            chart_id=chart_id,
            feature_type=FeatureType.GROWTH.value,
        )

        # If not unlocked and not admin, check for sufficient credits
        if not feature_unlocked and not current_user.is_admin:
            has_credits, required, available = await credit_service.has_sufficient_credits(
                db=db,
                user_id=current_user.id,
                feature_type=FeatureType.GROWTH.value,
            )
            # Unlimited plans have available == -1
            if available != -1 and not has_credits:
                cost = get_feature_cost(FeatureType.GROWTH.value)
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "insufficient_credits",
                        "message": f"This feature requires {required} credits. You have {available} credits available.",
                        "feature_type": FeatureType.GROWTH.value,
                        "required_credits": required,
                        "available_credits": available,
                        "feature_cost": cost,
                    },
                )

        # Initialize growth service with user's language and db for caching
        growth_service = PersonalGrowthService(language=user_language, db=db)

        # Extract focus areas from request body if provided
        focus_areas = body.focus_areas if body else None

        # Generate suggestions (with chart_id for dual persistence)
        suggestions = await growth_service.generate_growth_suggestions(
            chart_data=chart.chart_data,
            chart_id=chart_id,  # Enable persistence to ChartInterpretation table
            focus_areas=focus_areas,
        )

        # Cache the result in chart_data (flat format for consistency)
        chart.chart_data["growth_suggestions"] = suggestions
        await db.commit()

        # Consume credits only if not previously unlocked
        if not feature_unlocked:
            await credit_service.consume_credits(
                db=db,
                user_id=current_user.id,
                feature_type=FeatureType.GROWTH.value,
                resource_id=chart_id,
                description=f"Growth suggestions for chart {chart.person_name}",
            )

        logger.info(
            "Generated growth suggestions for chart {} (user: {}, language: {})",
            chart_id,
            current_user.email,
            user_language,
        )

        # Convert to response model
        return GrowthSuggestionsResponse(**suggestions)

    except chart_service.ChartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except chart_service.UnauthorizedAccessError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Error generating growth suggestions for chart {}: {}",
            chart_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating growth suggestions. Please try again.",
        ) from e
