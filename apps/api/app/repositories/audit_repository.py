"""
Audit Log repository.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog model."""

    def __init__(self, db: AsyncSession):
        """Initialize Audit repository."""
        super().__init__(AuditLog, db)

    async def create_log(
        self,
        user_id: UUID | None,
        action: str,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        extra_data: dict | None = None,
    ) -> AuditLog:
        """
        Create a new audit log entry.

        Args:
            user_id: User ID (optional for anonymous actions)
            action: Action performed (e.g., 'login', 'create_chart')
            resource_type: Type of resource (e.g., 'user', 'chart')
            resource_id: Resource UUID
            ip_address: IP address of request
            user_agent: User agent string
            extra_data: Additional data as JSONB

        Returns:
            Created audit log entry
        """
        from uuid import uuid4

        log = AuditLog(
            id=uuid4(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data,
        )

        return await self.create(log)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific user.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_action(
        self,
        action: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get audit logs by action type.

        Args:
            action: Action to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        conditions = [AuditLog.action == action]

        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)

        stmt = (
            select(AuditLog)
            .where(and_(*conditions))
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get audit logs for a specific resource.

        Args:
            resource_type: Type of resource (e.g., 'chart', 'user')
            resource_id: Resource UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
