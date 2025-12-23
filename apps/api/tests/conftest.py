"""
Test configuration and fixtures.

This module provides pytest fixtures and configuration for the test suite.
"""

import os

# IMPORTANT: Set environment variables BEFORE any app imports
# This ensures rate limiting is disabled before the limiter is initialized
os.environ["RATE_LIMIT_ENABLED"] = "false"

import asyncio  # noqa: E402
from collections.abc import AsyncGenerator  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402
from httpx import AsyncClient  # noqa: E402
from redis import asyncio as aioredis  # noqa: E402
from sqlalchemy import delete  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.main import app  # noqa: E402
from app.models.chart import AuditLog, BirthChart  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import OAuthAccount, User  # noqa: E402

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
async def db_session() -> AsyncGenerator[AsyncSession, None]:  # type: ignore[misc]  # noqa: UP043
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


# Test Redis URL (use DB 1 instead of DB 0 for test isolation)
TEST_REDIS_URL = str(settings.REDIS_URL).rsplit("/", 1)[0] + "/1"


@pytest.fixture(autouse=True)
async def reset_rate_limits():
    """
    Reset rate limits before and after each test by clearing test Redis database.

    Uses Redis DB 1 for test isolation (production uses DB 0).
    """
    # Connect to test Redis (DB 1)
    redis = await aioredis.from_url(TEST_REDIS_URL, decode_responses=True)

    try:
        # Clear all keys in test database before test
        await redis.flushdb()

        yield

        # Clear all keys in test database after test (cleanup)
        await redis.flushdb()

    finally:
        await redis.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:  # type: ignore[misc]  # noqa: UP043
    """
    Create an async HTTP client for testing.

    Overrides the app's get_db dependency to use the test database session.
    Rate limiting is disabled via RATE_LIMIT_ENABLED=False in settings.
    """
    from app.core.dependencies import get_db
    from app.core.rate_limit import limiter

    async def override_get_db():
        yield db_session

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Ensure rate limiting is disabled for tests
    # The limiter was already created with enabled=False due to settings
    # but we double-check here
    limiter.enabled = False

    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


# ===== Factory Fixtures =====


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user.

    Default credentials:
    - email: test@example.com
    - password: Test123!@#
    """
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Test User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
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
        admin = await test_user_factory(email="admin@realastrology.ai", role="admin")
    """

    async def _create_user(
        email: str = "test@example.com",
        password: str = "Test123!@#",
        full_name: str = "Test User",
        email_verified: bool = True,
        is_active: bool = True,
        is_superuser: bool = False,
        role: str = UserRole.FREE.value,
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
            role=role,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            **kwargs,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    """
    Create a test admin user.

    Default credentials:
    - email: admin@realastrology.ai
    - password: Admin123!@#
    - role: admin
    """
    user = User(
        id=uuid4(),
        email="admin@realastrology.ai",
        password_hash=get_password_hash("Admin123!@#"),
        full_name="Admin User",
        email_verified=True,
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_auth_headers(test_admin_user: User) -> dict[str, str]:
    """
    Get authentication headers for admin user.

    Returns headers dict with Bearer token.
    """
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_unverified_admin_user(db_session: AsyncSession) -> User:
    """
    Create a test admin user with unverified email.

    Default credentials:
    - email: unverified-admin@realastrology.ai
    - password: Admin123!@#
    - role: admin
    - email_verified: False
    """
    user = User(
        id=uuid4(),
        email="unverified-admin@realastrology.ai",
        password_hash=get_password_hash("Admin123!@#"),
        full_name="Unverified Admin User",
        email_verified=False,  # Email not verified
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def unverified_admin_auth_headers(test_unverified_admin_user: User) -> dict[str, str]:
    """
    Get authentication headers for unverified admin user.

    Returns headers dict with Bearer token.
    """
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_unverified_admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_chart_data() -> dict:
    """Sample chart calculation result for testing (language-first format)."""
    base_data = {
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
    # Return language-first format
    return {
        "en-US": base_data,
        "pt-BR": base_data,
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
        birth_datetime: datetime = datetime(1990, 1, 1, 12, 0, tzinfo=UTC),
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
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
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


@pytest.fixture
async def test_user_with_oauth(db_session: AsyncSession, test_user: User) -> User:
    """
    Create a test user with an OAuth connection.

    The user has both a password and a Google OAuth connection,
    allowing them to disconnect OAuth without losing access.
    """
    oauth_account = OAuthAccount(
        user_id=test_user.id,
        provider="google",
        provider_user_id="google_123456789",
        created_at=datetime.now(UTC),
    )
    db_session.add(oauth_account)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture
async def test_user_with_deletion_request(db_session: AsyncSession, test_user: User) -> User:
    """
    Create a test user with a pending account deletion request.

    The user has deleted_at set to simulate a scheduled deletion.
    """
    test_user.deleted_at = datetime.now(UTC)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user
