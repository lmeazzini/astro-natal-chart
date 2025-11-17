"""
Test configuration and fixtures.

This module provides pytest fixtures and configuration for the test suite.
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from redis import asyncio as aioredis
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.main import app
from app.models.chart import AuditLog, BirthChart
from app.models.user import OAuthAccount, User


# Create test database engine
test_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create test database tables before all tests and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a clean database session for each test.

    Uses transaction rollback for fast test isolation.
    """
    # Create a connection
    connection = await test_engine.connect()

    # Start a transaction
    transaction = await connection.begin()

    # Create a session bound to this transaction
    session = AsyncSession(bind=connection, expire_on_commit=False)

    # Clean all tables at the start
    await session.execute(delete(AuditLog))
    await session.execute(delete(BirthChart))
    await session.execute(delete(OAuthAccount))
    await session.execute(delete(User))
    await session.commit()

    yield session

    # Rollback transaction to clean up any changes
    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(autouse=True)
async def reset_rate_limits():
    """Reset rate limits before each test by clearing Redis."""
    # Connect to Redis
    redis = await aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)

    try:
        # Clear all rate limit keys (they start with "LIMITER")
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="LIMITER*", count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break

        yield

    finally:
        await redis.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing.

    Overrides the app's get_db dependency to use the test database session.
    """
    from app.core.dependencies import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ===== Factory Fixtures =====


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user.

    Default credentials:
    - email: test@realastrology.ai
    - password: Test123!@#
    """
    user = User(
        id=uuid4(),
        email="test@realastrology.ai",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Test User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_factory(db_session: AsyncSession):
    """
    Factory to create multiple test users.

    Usage:
        user1 = await test_user_factory(email="user1@example.com")
        user2 = await test_user_factory(email="user2@example.com", is_superuser=True)
    """
    async def _create_user(
        email: str = "test@realastrology.ai",
        password: str = "Test123!@#",
        full_name: str = "Test User",
        email_verified: bool = True,
        is_active: bool = True,
        is_superuser: bool = False,
        **kwargs,
    ) -> User:
        user = User(
            id=uuid4(),
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            email_verified=email_verified,
            is_active=is_active,
            is_superuser=is_superuser,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **kwargs,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def test_chart_data() -> dict:
    """Sample chart calculation result for testing."""
    return {
        "planets": [
            {
                "name": "Sun",
                "longitude": 45.123,
                "latitude": 0.002,
                "speed": 0.985,
                "retrograde": False,
                "sign": "Taurus",
                "degree": 15.123,
                "house": 10,
            },
            {
                "name": "Moon",
                "longitude": 165.456,
                "latitude": 5.234,
                "speed": 13.456,
                "retrograde": False,
                "sign": "Virgo",
                "degree": 15.456,
                "house": 3,
            },
        ],
        "houses": [
            {"number": 1, "cusp": 123.456, "sign": "Leo"},
            {"number": 2, "cusp": 153.456, "sign": "Virgo"},
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect": "trine",
                "angle": 120.0,
                "orb": 2.3,
                "applying": True,
            }
        ],
        "chart_info": {
            "ascendant": 123.456,
            "mc": 234.567,
            "ic": 54.567,
            "descendant": 303.456,
        },
    }


@pytest.fixture
async def test_chart_factory(db_session: AsyncSession, test_chart_data: dict):
    """
    Factory to create test birth charts.

    Usage:
        chart = await test_chart_factory(
            user=test_user,
            person_name="John Doe",
            birth_datetime=datetime(1990, 1, 1, 12, 0),
        )
    """
    async def _create_chart(
        user: User,
        person_name: str = "Test Person",
        birth_datetime: datetime = datetime(1990, 1, 1, 12, 0, tzinfo=timezone.utc),
        birth_timezone: str = "America/Sao_Paulo",
        latitude: float = -23.5505,
        longitude: float = -46.6333,
        city: str = "São Paulo",
        country: str = "Brazil",
        chart_data: dict | None = None,
        house_system: str = "placidus",
        **kwargs,
    ) -> BirthChart:
        chart = BirthChart(
            id=uuid4(),
            user_id=user.id,
            person_name=person_name,
            birth_datetime=birth_datetime,
            birth_timezone=birth_timezone,
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country,
            chart_data=chart_data or test_chart_data,
            house_system=house_system,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **kwargs,
        )
        db_session.add(chart)
        await db_session.commit()
        await db_session.refresh(chart)
        return chart

    return _create_chart


@pytest.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """
    Get authentication headers for test user.

    Returns headers dict with Bearer token.
    """
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}
