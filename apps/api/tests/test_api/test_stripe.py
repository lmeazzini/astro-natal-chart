"""Tests for Stripe payment API endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PlanType, SubscriptionStatus, UserRole
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.user import User


@pytest.fixture
async def premium_user_with_subscription(db_session: AsyncSession) -> tuple[User, Subscription]:
    """Create premium user with active Stripe subscription."""
    from app.repositories.subscription_repository import SubscriptionRepository
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)

    # Create user
    user = User(
        id=uuid4(),
        email="premium@test.com",
        password_hash="hashed",
        full_name="Premium User",
        role=UserRole.PREMIUM.value,
        email_verified=True,
        is_active=True,
    )
    created_user = await user_repo.create(user)

    # Create subscription with Stripe fields
    now = datetime.now(UTC)
    subscription = Subscription(
        id=uuid4(),
        user_id=created_user.id,
        status=SubscriptionStatus.ACTIVE.value,
        plan_type=PlanType.PRO.value,
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        stripe_price_id="price_pro123",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
        started_at=now,
        expires_at=now + timedelta(days=30),
    )
    created_sub = await subscription_repo.create(subscription)
    await db_session.commit()

    return created_user, created_sub


@pytest.fixture
def premium_headers(premium_user_with_subscription: tuple[User, Subscription]) -> dict[str, str]:
    """Generate authentication headers for premium user."""
    from app.core.security import create_access_token

    user, _ = premium_user_with_subscription
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def user_headers(test_user: User) -> dict[str, str]:
    """Generate authentication headers for regular user."""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


class TestGetStripeConfig:
    """Tests for GET /stripe/config endpoint."""

    async def test_get_config_success(self, client: AsyncClient):
        """Test getting public Stripe configuration."""
        response = await client.get("/api/v1/stripe/config")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "publishable_key" in data
        assert "enabled" in data
        assert "plans" in data

        # Verify plans structure
        plans = data["plans"]
        assert "starter" in plans
        assert "pro" in plans
        assert "unlimited" in plans

        # Verify plan details
        for _plan_name, plan_info in plans.items():
            assert "name" in plan_info
            assert "credits" in plan_info
            assert "price_brl" in plan_info

    async def test_get_config_no_auth_required(self, client: AsyncClient):
        """Test that config endpoint doesn't require authentication."""
        response = await client.get("/api/v1/stripe/config")
        assert response.status_code == 200


class TestCreateCheckoutSession:
    """Tests for POST /stripe/create-checkout-session endpoint."""

    async def test_create_checkout_requires_auth(self, client: AsyncClient):
        """Test that checkout requires authentication."""
        response = await client.post(
            "/api/v1/stripe/create-checkout-session",
            json={"plan_type": "pro"},
        )
        assert response.status_code == 401

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_checkout_stripe_disabled(
        self, mock_stripe_service: MagicMock, client: AsyncClient, user_headers: dict
    ):
        """Test checkout when Stripe is disabled."""
        mock_stripe_service.enabled = False

        response = await client.post(
            "/api/v1/stripe/create-checkout-session",
            json={"plan_type": "pro"},
            headers=user_headers,
        )

        assert response.status_code == 503
        assert "not configured" in response.json()["detail"].lower()

    async def test_create_checkout_invalid_plan(self, client: AsyncClient, user_headers: dict):
        """Test checkout with invalid plan type."""
        response = await client.post(
            "/api/v1/stripe/create-checkout-session",
            json={"plan_type": "invalid_plan"},
            headers=user_headers,
        )

        # Pydantic validates the enum before the endpoint runs
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_checkout_already_subscribed(
        self,
        mock_stripe_service: MagicMock,
        client: AsyncClient,
        premium_headers: dict,
    ):
        """Test checkout when user already has subscription."""
        mock_stripe_service.enabled = True
        mock_stripe_service.get_price_id_for_plan.return_value = "price_pro123"

        response = await client.post(
            "/api/v1/stripe/create-checkout-session",
            json={"plan_type": "pro"},
            headers=premium_headers,
        )

        assert response.status_code == 400
        assert "already have" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_checkout_success(
        self, mock_stripe_service: MagicMock, client: AsyncClient, user_headers: dict
    ):
        """Test successful checkout session creation."""
        mock_stripe_service.enabled = True
        mock_stripe_service.get_price_id_for_plan.return_value = "price_pro123"
        mock_stripe_service.get_or_create_customer.return_value = "cus_new123"
        mock_stripe_service.create_checkout_session.return_value = {
            "session_id": "cs_test123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test123",
        }

        response = await client.post(
            "/api/v1/stripe/create-checkout-session",
            json={"plan_type": "pro"},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "cs_test123"
        assert "checkout.stripe.com" in data["checkout_url"]


class TestCreatePortalSession:
    """Tests for POST /stripe/create-portal-session endpoint."""

    async def test_create_portal_requires_auth(self, client: AsyncClient):
        """Test that portal requires authentication."""
        response = await client.post(
            "/api/v1/stripe/create-portal-session",
            json={},
        )
        assert response.status_code == 401

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_portal_stripe_disabled(
        self, mock_stripe_service: MagicMock, client: AsyncClient, user_headers: dict
    ):
        """Test portal when Stripe is disabled."""
        mock_stripe_service.enabled = False

        response = await client.post(
            "/api/v1/stripe/create-portal-session",
            json={},
            headers=user_headers,
        )

        assert response.status_code == 503

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_portal_no_subscription(
        self, mock_stripe_service: MagicMock, client: AsyncClient, user_headers: dict
    ):
        """Test portal when user has no subscription."""
        mock_stripe_service.enabled = True

        response = await client.post(
            "/api/v1/stripe/create-portal-session",
            json={},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "no billing account" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_create_portal_success(
        self, mock_stripe_service: MagicMock, client: AsyncClient, premium_headers: dict
    ):
        """Test successful portal session creation."""
        mock_stripe_service.enabled = True
        mock_stripe_service.create_portal_session.return_value = (
            "https://billing.stripe.com/session/test"
        )

        response = await client.post(
            "/api/v1/stripe/create-portal-session",
            json={},
            headers=premium_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "billing.stripe.com" in data["portal_url"]


class TestSubscriptionStatus:
    """Tests for GET /stripe/subscription-status endpoint."""

    async def test_status_requires_auth(self, client: AsyncClient):
        """Test that status requires authentication."""
        response = await client.get("/api/v1/stripe/subscription-status")
        assert response.status_code == 401

    async def test_status_no_subscription(self, client: AsyncClient, user_headers: dict):
        """Test status when user has no subscription."""
        response = await client.get(
            "/api/v1/stripe/subscription-status",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_subscription"] is False
        assert data["plan_type"] == "free"

    async def test_status_with_subscription(self, client: AsyncClient, premium_headers: dict):
        """Test status when user has active subscription."""
        response = await client.get(
            "/api/v1/stripe/subscription-status",
            headers=premium_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_subscription"] is True
        assert data["plan_type"] == "pro"
        assert data["stripe_subscription_id"] == "sub_test123"
        assert data["days_until_renewal"] is not None
        assert data["days_until_renewal"] >= 0


class TestCancelSubscription:
    """Tests for POST /stripe/cancel-subscription endpoint."""

    async def test_cancel_requires_auth(self, client: AsyncClient):
        """Test that cancel requires authentication."""
        response = await client.post(
            "/api/v1/stripe/cancel-subscription",
            json={"at_period_end": True},
        )
        assert response.status_code == 401

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_cancel_stripe_disabled(
        self, mock_stripe_service: MagicMock, client: AsyncClient, premium_headers: dict
    ):
        """Test cancel when Stripe is disabled."""
        mock_stripe_service.enabled = False

        response = await client.post(
            "/api/v1/stripe/cancel-subscription",
            json={"at_period_end": True},
            headers=premium_headers,
        )

        assert response.status_code == 503

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_cancel_no_subscription(
        self, mock_stripe_service: MagicMock, client: AsyncClient, user_headers: dict
    ):
        """Test cancel when user has no subscription."""
        mock_stripe_service.enabled = True

        response = await client.post(
            "/api/v1/stripe/cancel-subscription",
            json={"at_period_end": True},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "no active subscription" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_cancel_at_period_end_success(
        self, mock_stripe_service: MagicMock, client: AsyncClient, premium_headers: dict
    ):
        """Test successful cancellation at period end."""
        mock_stripe_service.enabled = True

        response = await client.post(
            "/api/v1/stripe/cancel-subscription",
            json={"at_period_end": True},
            headers=premium_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["cancel_at_period_end"] is True
        assert "end of the billing period" in data["message"]


class TestReactivateSubscription:
    """Tests for POST /stripe/reactivate-subscription endpoint."""

    async def test_reactivate_requires_auth(self, client: AsyncClient):
        """Test that reactivate requires authentication."""
        response = await client.post("/api/v1/stripe/reactivate-subscription")
        assert response.status_code == 401

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_reactivate_not_cancelled(
        self, mock_stripe_service: MagicMock, client: AsyncClient, premium_headers: dict
    ):
        """Test reactivate when subscription is not scheduled for cancellation."""
        mock_stripe_service.enabled = True

        response = await client.post(
            "/api/v1/stripe/reactivate-subscription",
            headers=premium_headers,
        )

        assert response.status_code == 400
        assert "not scheduled for cancellation" in response.json()["detail"].lower()


class TestPaymentHistory:
    """Tests for GET /stripe/payment-history endpoint."""

    async def test_history_requires_auth(self, client: AsyncClient):
        """Test that payment history requires authentication."""
        response = await client.get("/api/v1/stripe/payment-history")
        assert response.status_code == 401

    async def test_history_empty(self, client: AsyncClient, user_headers: dict):
        """Test payment history when no payments exist."""
        response = await client.get(
            "/api/v1/stripe/payment-history",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["payments"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    async def test_history_with_payments(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user_with_subscription: tuple[User, Subscription],
    ):
        """Test payment history with payments."""
        from app.core.security import create_access_token
        from app.repositories.payment_repository import PaymentRepository

        user, subscription = premium_user_with_subscription
        payment_repo = PaymentRepository(db_session)

        # Create some payments
        for i in range(3):
            payment = Payment(
                id=uuid4(),
                user_id=user.id,
                subscription_id=subscription.id,
                stripe_payment_intent_id=f"pi_test{i}",
                stripe_invoice_id=f"in_test{i}",
                amount=4990,
                currency="brl",
                status="succeeded",
            )
            await payment_repo.create(payment)
        await db_session.commit()

        access_token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(
            "/api/v1/stripe/payment-history",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["payments"]) == 3
        assert data["total"] == 3

    async def test_history_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user_with_subscription: tuple[User, Subscription],
    ):
        """Test payment history pagination."""
        from app.core.security import create_access_token
        from app.repositories.payment_repository import PaymentRepository

        user, subscription = premium_user_with_subscription
        payment_repo = PaymentRepository(db_session)

        # Create 5 payments
        for i in range(5):
            payment = Payment(
                id=uuid4(),
                user_id=user.id,
                subscription_id=subscription.id,
                stripe_payment_intent_id=f"pi_page{i}",
                amount=4990,
                currency="brl",
                status="succeeded",
            )
            await payment_repo.create(payment)
        await db_session.commit()

        access_token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        # First page
        response = await client.get(
            "/api/v1/stripe/payment-history?page=1&page_size=2",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["payments"]) == 2
        assert data["has_more"] is True

        # Second page
        response = await client.get(
            "/api/v1/stripe/payment-history?page=2&page_size=2",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["payments"]) == 2
        assert data["has_more"] is True


class TestWebhook:
    """Tests for POST /stripe/webhooks endpoint."""

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_webhook_stripe_disabled(
        self, mock_stripe_service: MagicMock, client: AsyncClient
    ):
        """Test webhook when Stripe is disabled."""
        mock_stripe_service.enabled = False

        response = await client.post(
            "/api/v1/stripe/webhooks",
            content=b"{}",
            headers={"Stripe-Signature": "test_signature"},
        )

        assert response.status_code == 503

    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_webhook_invalid_signature(
        self, mock_stripe_service: MagicMock, client: AsyncClient
    ):
        """Test webhook with invalid signature."""
        mock_stripe_service.enabled = True
        mock_stripe_service.construct_webhook_event.side_effect = Exception("Invalid signature")

        response = await client.post(
            "/api/v1/stripe/webhooks",
            content=b"{}",
            headers={"Stripe-Signature": "invalid_signature"},
        )

        assert response.status_code == 400
        assert "invalid signature" in response.json()["detail"].lower()

    @patch("app.api.v1.endpoints.stripe.process_webhook_event")
    @patch("app.api.v1.endpoints.stripe.stripe_service")
    async def test_webhook_success(
        self,
        mock_stripe_service: MagicMock,
        mock_process: AsyncMock,
        client: AsyncClient,
    ):
        """Test successful webhook processing."""
        mock_stripe_service.enabled = True

        # Create mock event
        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event.id = "evt_test123"
        mock_stripe_service.construct_webhook_event.return_value = mock_event

        mock_process.return_value = {"status": "success"}

        response = await client.post(
            "/api/v1/stripe/webhooks",
            content=b'{"type": "checkout.session.completed"}',
            headers={"Stripe-Signature": "valid_signature"},
        )

        assert response.status_code == 200
        mock_process.assert_called_once()
