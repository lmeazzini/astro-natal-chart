"""
Base repository with common CRUD operations.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common database operations."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Get entity by ID.

        Args:
            id: Entity UUID

        Returns:
            Entity instance or None if not found
        """
        stmt = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """
        Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        """
        Create new entity.

        Args:
            entity: Entity instance to create

        Returns:
            Created entity with populated fields
        """
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """
        Update existing entity.

        Args:
            entity: Entity instance to update

        Returns:
            Updated entity
        """
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """
        Delete entity.

        Args:
            entity: Entity instance to delete
        """
        await self.db.delete(entity)
        await self.db.commit()

    async def flush(self) -> None:
        """Flush changes to database without committing."""
        await self.db.flush()

    async def commit(self) -> None:
        """Commit transaction."""
        await self.db.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.db.rollback()
