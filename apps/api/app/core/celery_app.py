"""
Celery application configuration.
"""

from celery import Celery
from celery.schedules import crontab  # type: ignore[import-untyped]

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "astro_worker",
    broker=str(settings.REDIS_URL) if settings.REDIS_URL else "redis://localhost:6379/0",
    backend=str(settings.REDIS_URL) if settings.REDIS_URL else "redis://localhost:6379/0",
    include=[
        "app.tasks.astro_tasks",
        "app.tasks.cache_tasks",
        "app.tasks.pdf_tasks",
        "app.tasks.privacy",
    ],
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time for heavy tasks
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)

# Periodic tasks schedule (Beat)
celery_app.conf.beat_schedule = {
    # Hard delete de usuários marcados há 30+ dias
    "cleanup-deleted-users-daily": {
        "task": "privacy.cleanup_deleted_users",
        "schedule": crontab(hour=3, minute=0),  # 3h AM diariamente
    },
    # Limpar tokens de reset de senha expirados (24h+)
    "cleanup-expired-password-reset-tokens-daily": {
        "task": "privacy.cleanup_expired_password_reset_tokens",
        "schedule": crontab(hour=4, minute=0),  # 4h AM diariamente
    },
    # Limpar cache de interpretações expirado (30+ dias sem acesso)
    "cleanup-expired-interpretation-cache-daily": {
        "task": "cache.cleanup_expired_interpretations",
        "schedule": crontab(hour=5, minute=0),  # 5h AM diariamente
        "kwargs": {"ttl_days": 30},
    },
}
