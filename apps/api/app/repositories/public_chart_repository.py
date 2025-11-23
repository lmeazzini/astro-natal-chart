"""
Public Chart repository.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.public_chart import PublicChart
from app.repositories.base import BaseRepository


class PublicChartRepository(BaseRepository[PublicChart]):
    """Repository for PublicChart model."""

    def __init__(self, db: AsyncSession):
        """Initialize PublicChart repository."""
        super().__init__(PublicChart, db)

    async def get_by_slug(self, slug: str) -> PublicChart | None:
        """
        Get public chart by slug.

        Args:
            slug: URL-friendly identifier

        Returns:
            PublicChart instance or None if not found
        """
        stmt = select(PublicChart).where(PublicChart.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published_by_slug(self, slug: str) -> PublicChart | None:
        """
        Get published public chart by slug.

        Args:
            slug: URL-friendly identifier

        Returns:
            PublicChart instance or None if not found/unpublished
        """
        stmt = select(PublicChart).where(
            PublicChart.slug == slug,
            PublicChart.is_published.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_published(
        self,
        category: str | None = None,
        search: str | None = None,
        sort: str = "name",
        skip: int = 0,
        limit: int = 20,
    ) -> list[PublicChart]:
        """
        Get all published public charts with filters.

        Args:
            category: Filter by category
            search: Search term for name
            sort: Sort order ('name', 'date', 'views')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public charts
        """
        conditions: list = [PublicChart.is_published.is_(True)]

        if category:
            conditions.append(PublicChart.category == category)

        if search:
            conditions.append(PublicChart.full_name.ilike(f"%{search}%"))

        stmt = select(PublicChart).where(*conditions)

        # Apply sorting
        if sort == "date":
            stmt = stmt.order_by(PublicChart.birth_datetime.desc())
        elif sort == "views":
            stmt = stmt.order_by(PublicChart.view_count.desc())
        else:  # name (default)
            stmt = stmt.order_by(PublicChart.full_name.asc())

        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_published(
        self,
        category: str | None = None,
        search: str | None = None,
    ) -> int:
        """
        Count total published public charts with filters.

        Args:
            category: Filter by category
            search: Search term for name

        Returns:
            Total count
        """
        conditions: list = [PublicChart.is_published.is_(True)]

        if category:
            conditions.append(PublicChart.category == category)

        if search:
            conditions.append(PublicChart.full_name.ilike(f"%{search}%"))

        stmt = select(func.count()).select_from(PublicChart).where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_featured(self, limit: int = 10) -> list[PublicChart]:
        """
        Get featured public charts.

        Args:
            limit: Maximum number of charts to return

        Returns:
            List of featured charts
        """
        stmt = (
            select(PublicChart)
            .where(
                PublicChart.is_published.is_(True),
                PublicChart.featured.is_(True),
            )
            .order_by(PublicChart.view_count.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[PublicChart]:
        """
        Get all published charts in a category.

        Args:
            category: Category to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of charts in the category
        """
        stmt = (
            select(PublicChart)
            .where(
                PublicChart.is_published.is_(True),
                PublicChart.category == category,
            )
            .order_by(PublicChart.full_name.asc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def increment_view_count(self, chart: PublicChart) -> PublicChart:
        """
        Increment the view count for a chart.

        Args:
            chart: PublicChart instance

        Returns:
            Updated PublicChart instance
        """
        chart.view_count = chart.view_count + 1
        await self.db.commit()
        await self.db.refresh(chart)
        return chart

    async def get_all_admin(
        self,
        skip: int = 0,
        limit: int = 50,
        include_unpublished: bool = True,
    ) -> list[PublicChart]:
        """
        Get all public charts (admin view).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_unpublished: Include unpublished charts

        Returns:
            List of all charts
        """
        stmt = select(PublicChart)

        if not include_unpublished:
            stmt = stmt.where(PublicChart.is_published.is_(True))

        stmt = stmt.order_by(PublicChart.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self, include_unpublished: bool = True) -> int:
        """
        Count total public charts (admin).

        Args:
            include_unpublished: Include unpublished charts

        Returns:
            Total count
        """
        stmt = select(func.count()).select_from(PublicChart)

        if not include_unpublished:
            stmt = stmt.where(PublicChart.is_published.is_(True))

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """
        Check if a slug already exists.

        Args:
            slug: Slug to check
            exclude_id: Optional ID to exclude from check (for updates)

        Returns:
            True if slug exists
        """
        conditions = [PublicChart.slug == slug]

        if exclude_id:
            conditions.append(PublicChart.id != exclude_id)

        stmt = select(func.count()).select_from(PublicChart).where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
