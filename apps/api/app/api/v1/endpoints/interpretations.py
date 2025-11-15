"""
Chart interpretation endpoints for AI-generated astrological interpretations.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.interpretation import ChartInterpretationsResponse
from app.services import chart_service
from app.services.interpretation_service import InterpretationService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/charts/{chart_id}/interpretations",
    response_model=ChartInterpretationsResponse,
    summary="Get chart interpretations",
    description="Get all AI-generated interpretations for a birth chart (classical 7 planets only).",
)
async def get_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartInterpretationsResponse:
    """
    Get all interpretations for a birth chart.

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chart interpretations grouped by type (planets, houses, aspects)

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
        # Verify user owns the chart
        await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Get interpretations
        interpretation_service = InterpretationService(db)
        interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

        return ChartInterpretationsResponse(**interpretations)

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
    except Exception as e:
        logger.error(f"Error retrieving interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving interpretations",
        ) from e


@router.post(
    "/charts/{chart_id}/interpretations/regenerate",
    response_model=ChartInterpretationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate chart interpretations",
    description="Delete existing interpretations and generate new ones using OpenAI.",
)
async def regenerate_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartInterpretationsResponse:
    """
    Regenerate all interpretations for a birth chart.

    This endpoint:
    1. Verifies user owns the chart
    2. Deletes existing interpretations
    3. Generates new interpretations using OpenAI
    4. Returns the new interpretations

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Newly generated chart interpretations

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        interpretation_service = InterpretationService(db)

        # Delete existing interpretations
        deleted_count = await interpretation_service.repository.delete_by_chart_id(chart_id)
        logger.info(f"Deleted {deleted_count} existing interpretations for chart {chart_id}")

        # Generate new interpretations
        await interpretation_service.generate_all_interpretations(
            chart_id=chart_id,
            chart_data=chart.chart_data,
        )

        # Get and return new interpretations
        interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

        return ChartInterpretationsResponse(**interpretations)

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
    except Exception as e:
        logger.error(f"Error regenerating interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error regenerating interpretations",
        ) from e
