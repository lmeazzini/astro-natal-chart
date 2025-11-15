"""
Celery tasks for async processing.
"""

from app.tasks.privacy import cleanup_deleted_users

__all__ = ["cleanup_deleted_users"]
