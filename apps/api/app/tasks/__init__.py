"""
Celery tasks for async processing.
"""

from app.tasks.astro_tasks import generate_birth_chart_task, generate_secondary_language_task
from app.tasks.privacy import cleanup_deleted_users

__all__ = ["cleanup_deleted_users", "generate_birth_chart_task", "generate_secondary_language_task"]
