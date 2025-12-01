"""
Public Chart service for business logic.
"""

import re
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.public_chart import PublicChart
from app.repositories.public_chart_repository import PublicChartRepository
from app.schemas.public_chart import (
    PublicChartCreate,
    PublicChartDetail,
    PublicChartList,
    PublicChartPreview,
    PublicChartUpdate,
)
from app.services.astro_service import calculate_birth_chart


def generate_slug(name: str) -> str:
    """
    Generate a URL-friendly slug from a name.

    Args:
        name: Full name to convert

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    return slug


class PublicChartService:
    """Service for PublicChart business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize PublicChartService."""
        self.db = db
        self.repository = PublicChartRepository(db)

    async def create_chart(self, data: PublicChartCreate) -> PublicChart:
        """
        Create a new public chart.

        Args:
            data: Chart creation data

        Returns:
            Created PublicChart instance

        Raises:
            ValueError: If slug already exists
        """
        # Check if slug exists
        if await self.repository.slug_exists(data.slug):
            raise ValueError(f"Slug '{data.slug}' already exists")

        # Calculate chart data
        chart_data = calculate_birth_chart(
            birth_datetime=data.birth_datetime,
            timezone=data.birth_timezone,
            latitude=data.latitude,
            longitude=data.longitude,
            house_system=data.house_system,
        )

        # Create chart
        chart = PublicChart(
            slug=data.slug,
            full_name=data.full_name,
            category=data.category,
            birth_datetime=data.birth_datetime,
            birth_timezone=data.birth_timezone,
            latitude=data.latitude,
            longitude=data.longitude,
            city=data.city,
            country=data.country,
            chart_data=chart_data,
            house_system=data.house_system,
            photo_url=data.photo_url,
            # Legacy single-language fields
            short_bio=data.short_bio,
            highlights=data.highlights,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            meta_keywords=data.meta_keywords,
            # i18n multilingual fields
            short_bio_i18n=data.short_bio_i18n,
            highlights_i18n=data.highlights_i18n,
            meta_title_i18n=data.meta_title_i18n,
            meta_description_i18n=data.meta_description_i18n,
            meta_keywords_i18n=data.meta_keywords_i18n,
            is_published=data.is_published,
            featured=data.featured,
        )

        created_chart = await self.repository.create(chart)
        logger.info(f"Created public chart: {created_chart.full_name} ({created_chart.slug})")
        return created_chart

    async def get_chart_by_slug(
        self,
        slug: str,
        increment_views: bool = True,
    ) -> PublicChart | None:
        """
        Get a published public chart by slug.

        Args:
            slug: Chart slug
            increment_views: Whether to increment view count

        Returns:
            PublicChart instance or None
        """
        chart = await self.repository.get_published_by_slug(slug)

        if chart and increment_views:
            await self.repository.increment_view_count(chart)

        return chart

    async def get_chart_by_id(self, chart_id: UUID) -> PublicChart | None:
        """
        Get a public chart by ID (admin).

        Args:
            chart_id: Chart UUID

        Returns:
            PublicChart instance or None
        """
        return await self.repository.get_by_id(chart_id)

    async def list_charts(
        self,
        category: str | None = None,
        search: str | None = None,
        sort: str = "name",
        page: int = 1,
        page_size: int = 20,
    ) -> PublicChartList:
        """
        List published public charts with filters.

        Args:
            category: Filter by category
            search: Search term for name
            sort: Sort order ('name', 'date', 'views')
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Paginated list of charts
        """
        skip = (page - 1) * page_size

        charts = await self.repository.get_all_published(
            category=category,
            search=search,
            sort=sort,
            skip=skip,
            limit=page_size,
        )

        total = await self.repository.count_published(
            category=category,
            search=search,
        )

        return PublicChartList(
            charts=[PublicChartPreview.model_validate(c) for c in charts],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_featured_charts(self, limit: int = 10) -> list[PublicChartPreview]:
        """
        Get featured public charts.

        Args:
            limit: Maximum number of charts

        Returns:
            List of featured charts
        """
        charts = await self.repository.get_featured(limit=limit)
        return [PublicChartPreview.model_validate(c) for c in charts]

    async def update_chart(
        self,
        chart_id: UUID,
        data: PublicChartUpdate,
    ) -> PublicChart | None:
        """
        Update a public chart.

        Args:
            chart_id: Chart UUID
            data: Update data

        Returns:
            Updated PublicChart instance or None

        Raises:
            ValueError: If new slug already exists
        """
        chart = await self.repository.get_by_id(chart_id)
        if not chart:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Check if slug is being changed and if it exists
        if "slug" in update_data and update_data["slug"] != chart.slug:
            if await self.repository.slug_exists(update_data["slug"], exclude_id=chart_id):
                raise ValueError(f"Slug '{update_data['slug']}' already exists")

        # Check if birth data changed - need to recalculate
        birth_fields = ["birth_datetime", "birth_timezone", "latitude", "longitude", "house_system"]
        needs_recalculation = any(field in update_data for field in birth_fields)

        # Apply updates
        for field, value in update_data.items():
            setattr(chart, field, value)

        # Recalculate chart data if needed
        if needs_recalculation:
            chart_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system,
            )
            chart.chart_data = chart_data
            logger.info(f"Recalculated chart data for: {chart.full_name}")

        await self.db.commit()
        await self.db.refresh(chart)

        logger.info(f"Updated public chart: {chart.full_name} ({chart.slug})")
        return chart

    async def delete_chart(self, chart_id: UUID) -> bool:
        """
        Delete a public chart.

        Args:
            chart_id: Chart UUID

        Returns:
            True if deleted, False if not found
        """
        chart = await self.repository.get_by_id(chart_id)
        if not chart:
            return False

        await self.repository.delete(chart)
        logger.info(f"Deleted public chart: {chart.full_name} ({chart.slug})")
        return True

    async def list_charts_admin(
        self,
        page: int = 1,
        page_size: int = 50,
        include_unpublished: bool = True,
    ) -> PublicChartList:
        """
        List all public charts (admin view).

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            include_unpublished: Include unpublished charts

        Returns:
            Paginated list of all charts
        """
        skip = (page - 1) * page_size

        charts = await self.repository.get_all_admin(
            skip=skip,
            limit=page_size,
            include_unpublished=include_unpublished,
        )

        total = await self.repository.count_all(include_unpublished=include_unpublished)

        return PublicChartList(
            charts=[PublicChartPreview.model_validate(c) for c in charts],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_chart_detail(self, slug: str) -> PublicChartDetail | None:
        """
        Get full chart detail by slug.

        Args:
            slug: Chart slug

        Returns:
            Full chart detail or None
        """
        chart = await self.get_chart_by_slug(slug, increment_views=True)
        if not chart:
            return None

        return PublicChartDetail.model_validate(chart)

    async def get_categories_with_counts(self) -> list[dict[str, int | str]]:
        """
        Get all categories with chart counts.

        Returns:
            List of categories with counts
        """
        from sqlalchemy import func, select

        from app.models.public_chart import PublicChart

        stmt = (
            select(
                PublicChart.category,
                func.count(PublicChart.id).label("count"),
            )
            .where(
                PublicChart.is_published.is_(True),
                PublicChart.category.isnot(None),
            )
            .group_by(PublicChart.category)
            .order_by(func.count(PublicChart.id).desc())
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [{"category": row[0], "count": row[1]} for row in rows]
