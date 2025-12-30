"""
Database configuration and session management.
Uses SQLAlchemy 2.0 with async support.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:  # type: ignore[misc]  # noqa: UP043
    """
    Dependency to get database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connection pool."""
    await engine.dispose()


def create_task_local_session() -> tuple[async_sessionmaker[AsyncSession], AsyncEngine]:
    """
    Create a task-local async engine and session factory.

    This is required for Celery tasks that use asyncio.run() because each call
    creates a new event loop. The global engine's connection pool would hold
    connections bound to old/closed event loops, causing "Event loop is closed"
    and "Future attached to a different loop" errors.

    Usage in Celery tasks:
        async def my_async_task():
            TaskSessionLocal, task_engine = create_task_local_session()
            try:
                async with TaskSessionLocal() as session:
                    # ... use session
            finally:
                await task_engine.dispose()

    Returns:
        Tuple of (session_factory, engine) - caller must dispose engine when done
    """
    from sqlalchemy.pool import NullPool

    # Create a fresh engine with NullPool - no connection persistence
    # This ensures connections don't outlive the event loop
    task_engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DEBUG,
        poolclass=NullPool,  # No pooling - fresh connection each time
    )

    task_session_factory = async_sessionmaker(
        task_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    return task_session_factory, task_engine
