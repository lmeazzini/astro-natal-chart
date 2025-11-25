"""
Personal growth suggestions endpoints.

Provides AI-powered personal development suggestions based on natal chart analysis.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_verified_email
from app.core.i18n import normalize_locale
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.growth import (
    GrowthSuggestionsRequest,
    GrowthSuggestionsResponse,
)
from app.services import chart_service
from app.services.personal_growth_service import PersonalGrowthService

router = APIRouter()


@router.post(
    "/charts/{chart_id}/growth-suggestions",
    response_model=GrowthSuggestionsResponse,
    summary="Generate personal growth suggestions",
    description=(
        "Generate AI-powered personal development suggestions based on the natal chart. "
        "Includes growth points, challenges, opportunities, and life purpose insights. "
        "Requires verified email. Rate limited to 10 requests per hour."
    ),
    responses={
        403: {
            "description": "Email not verified or unauthorized access",
            "content": {
                "application/json": {
                    "examples": {
                        "email_not_verified": {
                            "summary": "Email not verified",
                            "value": {
                                "detail": {
                                    "error": "email_not_verified",
                                    "message": "Email verification required to access this feature.",
                                    "user_email": "user@example.com",
                                }
                            },
                        },
                        "unauthorized": {
                            "summary": "Unauthorized access",
                            "value": {"detail": "Not authorized to access this chart"},
                        },
                    }
                }
            },
        },
        404: {
            "description": "Chart not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Chart not found"}
                }
            },
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 10 per 1 hour"}
                }
            },
        },
    },
)
@limiter.limit(RateLimits.GROWTH_SUGGESTIONS)
async def generate_growth_suggestions(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_verified_email)],
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
        current_user: Current authenticated user (must have verified email)
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

        # Initialize growth service with user's language and db for caching
        growth_service = PersonalGrowthService(language=user_language, db=db)

        # Extract focus areas from request body if provided
        focus_areas = body.focus_areas if body else None

        # Generate suggestions
        suggestions = await growth_service.generate_growth_suggestions(
            chart_data=chart.chart_data,
            focus_areas=focus_areas,
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
