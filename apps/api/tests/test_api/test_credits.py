"""Tests for credits API endpoints."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import FeatureType, PlanType, TransactionType, UserRole
from app.models.user import User
from app.models.user_credit import UserCredit


@pytest.fixture
async def user_with_credits(db_session: AsyncSession, test_user: User) -> tuple[User, UserCredit]:
    """Create user with credits."""
    from app.repositories.credit_repository import CreditRepository

    credit_repo = CreditRepository(db_session)

    now = datetime.now(UTC)
    credit = UserCredit(
        id=uuid4(),
        user_id=test_user.id,
        plan_type=PlanType.FREE.value,
        credits_balance=8,
        credits_limit=10,
        period_start=now,
        period_end=now + timedelta(days=30),
    )
    await credit_repo.create(credit)
    await db_session.commit()

    return test_user, credit


@pytest.fixture
def user_with_credits_headers(user_with_credits: tuple[User, UserCredit]) -> dict[str, str]:
    """Generate authentication headers for user with credits."""
    from app.core.security import create_access_token

    user, _ = user_with_credits
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def unlimited_user(db_session: AsyncSession) -> tuple[User, UserCredit]:
    """Create user with unlimited credits."""
    from app.repositories.credit_repository import CreditRepository
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    credit_repo = CreditRepository(db_session)

    user = User(
        id=uuid4(),
        email="unlimited@test.com",
        password_hash="hashed",
        full_name="Unlimited User",
        role=UserRole.PREMIUM.value,
        email_verified=True,
        is_active=True,
    )
    created_user = await user_repo.create(user)

    now = datetime.now(UTC)
    credit = UserCredit(
        id=uuid4(),
        user_id=created_user.id,
        plan_type=PlanType.UNLIMITED.value,
        credits_balance=0,  # Doesn't matter for unlimited
        credits_limit=None,  # Unlimited
        period_start=now,
        period_end=now + timedelta(days=30),
    )
    await credit_repo.create(credit)
    await db_session.commit()

    return created_user, credit


@pytest.fixture
def user_headers(test_user: User) -> dict[str, str]:
    """Generate authentication headers for regular user."""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


class TestGetCredits:
    """Tests for GET /credits endpoint."""

    async def test_get_credits_requires_auth(self, client: AsyncClient):
        """Test that getting credits requires authentication."""
        response = await client.get("/api/v1/credits")
        assert response.status_code == 401

    async def test_get_credits_new_user(self, client: AsyncClient, user_headers: dict):
        """Test getting credits for new user (auto-allocates free credits)."""
        response = await client.get("/api/v1/credits", headers=user_headers)

        assert response.status_code == 200
        data = response.json()

        # Should auto-allocate free credits
        assert data["plan_type"] == "free"
        assert data["credits_balance"] == 10  # Free plan gives 10 credits
        assert data["credits_limit"] == 10
        assert data["is_unlimited"] is False

    async def test_get_credits_with_existing_credits(
        self, client: AsyncClient, user_with_credits_headers: dict
    ):
        """Test getting credits for user with existing credits."""
        response = await client.get("/api/v1/credits", headers=user_with_credits_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["plan_type"] == "free"
        assert data["credits_balance"] == 8
        assert data["credits_limit"] == 10
        assert data["is_unlimited"] is False
        assert data["period_end"] is not None

    async def test_get_credits_unlimited_user(
        self, client: AsyncClient, unlimited_user: tuple[User, UserCredit]
    ):
        """Test getting credits for unlimited user."""
        from app.core.security import create_access_token

        user, _ = unlimited_user
        access_token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get("/api/v1/credits", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["plan_type"] == "unlimited"
        assert data["credits_limit"] is None
        assert data["is_unlimited"] is True


class TestGetCreditHistory:
    """Tests for GET /credits/history endpoint."""

    async def test_history_requires_auth(self, client: AsyncClient):
        """Test that credit history requires authentication."""
        response = await client.get("/api/v1/credits/history")
        assert response.status_code == 401

    async def test_history_empty(self, client: AsyncClient, user_with_credits_headers: dict):
        """Test empty credit history."""
        response = await client.get("/api/v1/credits/history", headers=user_with_credits_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["transactions"] == []
        assert data["total"] == 0

    async def test_history_with_transactions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        user_with_credits: tuple[User, UserCredit],
    ):
        """Test credit history with transactions."""
        from app.core.security import create_access_token
        from app.models.credit_transaction import CreditTransaction

        user, credit = user_with_credits

        # Create some transactions
        for i in range(3):
            transaction = CreditTransaction(
                id=uuid4(),
                user_id=user.id,
                transaction_type=TransactionType.DEBIT.value,
                amount=1,
                balance_after=10 - (i + 1),
                feature_type=FeatureType.INTERPRETATION_BASIC.value,
            )
            db_session.add(transaction)
        await db_session.commit()

        access_token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get("/api/v1/credits/history", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert len(data["transactions"]) == 3
        assert data["total"] == 3


class TestGetCreditUsage:
    """Tests for GET /credits/usage endpoint."""

    async def test_usage_requires_auth(self, client: AsyncClient):
        """Test that credit usage requires authentication."""
        response = await client.get("/api/v1/credits/usage")
        assert response.status_code == 401

    async def test_usage_empty(self, client: AsyncClient, user_with_credits_headers: dict):
        """Test empty credit usage."""
        response = await client.get("/api/v1/credits/usage", headers=user_with_credits_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total_used"] == 0
        assert data["usage_by_feature"] == {}

    async def test_usage_with_transactions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        user_with_credits: tuple[User, UserCredit],
    ):
        """Test credit usage with transactions."""
        from app.core.security import create_access_token
        from app.models.credit_transaction import CreditTransaction

        user, credit = user_with_credits

        # Create transactions for different features
        transactions = [
            (TransactionType.DEBIT.value, FeatureType.INTERPRETATION_BASIC.value, 1),
            (TransactionType.DEBIT.value, FeatureType.INTERPRETATION_BASIC.value, 1),
            (TransactionType.DEBIT.value, FeatureType.PDF_REPORT.value, 2),
        ]

        for tx_type, feature, amount in transactions:
            transaction = CreditTransaction(
                id=uuid4(),
                user_id=user.id,
                transaction_type=tx_type,
                amount=amount,
                balance_after=8 - amount,
                feature_type=feature,
            )
            db_session.add(transaction)
        await db_session.commit()

        access_token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get("/api/v1/credits/usage", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Total of 4 credits used (2 + 2)
        assert data["total_used"] == 4
        assert "interpretation_basic" in data["usage_by_feature"]
        assert "pdf_report" in data["usage_by_feature"]


class TestCreditService:
    """Tests for credit_service functions."""

    async def test_allocate_credits_free_plan(self, db_session: AsyncSession, test_user: User):
        """Test allocating credits for free plan."""
        from app.services import credit_service

        credit = await credit_service.allocate_credits(
            db_session, test_user.id, PlanType.FREE.value
        )

        assert credit.plan_type == PlanType.FREE.value
        assert credit.credits_balance == 10
        assert credit.credits_limit == 10

    async def test_allocate_credits_unlimited_plan(self, db_session: AsyncSession, test_user: User):
        """Test allocating credits for unlimited plan."""
        from app.services import credit_service

        credit = await credit_service.allocate_credits(
            db_session, test_user.id, PlanType.UNLIMITED.value
        )

        assert credit.plan_type == PlanType.UNLIMITED.value
        assert credit.credits_limit is None

    async def test_consume_credits_success(
        self, db_session: AsyncSession, user_with_credits: tuple[User, UserCredit]
    ):
        """Test consuming credits successfully."""
        from app.services import credit_service

        user, credit = user_with_credits

        transaction = await credit_service.consume_credits(
            db_session, user.id, FeatureType.INTERPRETATION_BASIC.value
        )

        assert transaction.transaction_type == TransactionType.DEBIT.value
        # Basic interpretation costs 1 credit, amount is stored as negative
        assert transaction.amount == -1

        # Verify balance updated
        await db_session.refresh(credit)
        assert credit.credits_balance == 7  # 8 - 1

    async def test_consume_credits_insufficient(
        self, db_session: AsyncSession, user_with_credits: tuple[User, UserCredit]
    ):
        """Test consuming credits when insufficient."""
        from app.services import credit_service
        from app.services.credit_service import InsufficientCreditsError

        user, credit = user_with_credits

        # Set balance to 0
        credit.credits_balance = 0
        await db_session.commit()

        with pytest.raises(InsufficientCreditsError):
            await credit_service.consume_credits(db_session, user.id, FeatureType.PDF_REPORT.value)

    async def test_has_sufficient_credits(
        self, db_session: AsyncSession, user_with_credits: tuple[User, UserCredit]
    ):
        """Test checking sufficient credits."""
        from app.services import credit_service

        user, _ = user_with_credits

        # Should have enough for basic interpretation
        has_enough, required, available = await credit_service.has_sufficient_credits(
            db_session, user.id, FeatureType.INTERPRETATION_BASIC.value
        )
        assert has_enough is True
        assert required == 1
        assert available == 8

    async def test_unlimited_user_always_has_credits(
        self, db_session: AsyncSession, unlimited_user: tuple[User, UserCredit]
    ):
        """Test that unlimited user always has sufficient credits."""
        from app.services import credit_service

        user, _ = unlimited_user

        # Should always have enough credits
        has_enough, required, available = await credit_service.has_sufficient_credits(
            db_session, user.id, FeatureType.PDF_REPORT.value
        )
        assert has_enough is True
        assert available == -1  # -1 indicates unlimited

    async def test_reset_monthly_credits(
        self, db_session: AsyncSession, user_with_credits: tuple[User, UserCredit]
    ):
        """Test resetting monthly credits."""
        from app.services import credit_service

        user, credit = user_with_credits

        # Consume some credits
        credit.credits_balance = 5
        await db_session.commit()

        updated_credit = await credit_service.reset_monthly_credits(db_session, user.id)

        # Should be reset to full limit
        assert updated_credit.credits_balance == credit.credits_limit
