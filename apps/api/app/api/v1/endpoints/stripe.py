"""Stripe payment API endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.credit_config import CREDIT_PACKS
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.i18n import translate as _
from app.core.i18n.messages import StripeMessages
from app.models.enums import PlanType, SubscriptionStatus
from app.models.subscription import Subscription
from app.models.user import User
from app.repositories.payment_repository import PaymentRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.stripe import (
    CancelSubscriptionRequest,
    CancelSubscriptionResponse,
    CheckoutSessionResponse,
    CreateCheckoutSessionRequest,
    CreateCreditPurchaseRequest,
    CreatePortalSessionRequest,
    PaymentHistoryResponse,
    PaymentRead,
    PortalSessionResponse,
    StripeConfigResponse,
    SubscriptionStatusResponse,
)
from app.services.stripe_service import stripe_service
from app.services.stripe_webhook_handler import process_webhook_event

router = APIRouter(prefix="/stripe", tags=["Stripe Payments"])


@router.get(
    "/config",
    response_model=StripeConfigResponse,
    summary="Get Stripe public configuration",
)
async def get_stripe_config() -> StripeConfigResponse:
    """
    Get public Stripe configuration for frontend.

    Returns publishable key, plan pricing info, and credit pack info.
    """
    # Build credit packs with price IDs
    credit_packs_config = {}
    for pack_name, pack_info in CREDIT_PACKS.items():
        credit_packs_config[pack_name] = {
            "name": pack_info["name"],
            "credits": pack_info["credits"],
            "price_brl": pack_info["price_brl"],
            "price_id": stripe_service.get_credit_pack_price_id(pack_name),
        }

    return StripeConfigResponse(
        publishable_key=settings.STRIPE_PUBLISHABLE_KEY or "",
        enabled=stripe_service.enabled,
        plans={
            "starter": {
                "name": "Starter",
                "price_id": settings.STRIPE_PRICE_STARTER,
                "credits": 50,
                "price_brl": 3000,  # R$ 30,00 in cents
            },
            "pro": {
                "name": "Pro",
                "price_id": settings.STRIPE_PRICE_PRO,
                "credits": 200,
                "price_brl": 10000,  # R$ 100,00 in cents
            },
            "unlimited": {
                "name": "Unlimited",
                "price_id": settings.STRIPE_PRICE_UNLIMITED,
                "credits": None,  # Unlimited
                "price_brl": 50000,  # R$ 500,00 in cents
            },
        },
        credit_packs=credit_packs_config,
    )


@router.post(
    "/create-checkout-session",
    response_model=CheckoutSessionResponse,
    summary="Create Stripe checkout session",
)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout session for subscription purchase.

    Redirects user to Stripe's hosted checkout page.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    # Validate plan type
    if request.plan_type not in [
        PlanType.STARTER.value,
        PlanType.PRO.value,
        PlanType.UNLIMITED.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.INVALID_PLAN_TYPE, plan_type=request.plan_type),
        )

    # Get price ID for plan
    price_id = stripe_service.get_price_id_for_plan(request.plan_type)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.PRICE_NOT_CONFIGURED, plan_type=request.plan_type),
        )

    # Check if user already has active subscription
    subscription_repo = SubscriptionRepository(db)
    existing = await subscription_repo.get_by_user_id(current_user.id)
    if existing and existing.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.ALREADY_SUBSCRIBED),
        )

    # Get or create Stripe customer
    customer_id = stripe_service.get_or_create_customer(
        user_id=str(current_user.id),
        email=current_user.email,
        name=current_user.full_name,
    )

    # Store customer ID if new
    if existing and not existing.stripe_customer_id:
        existing.stripe_customer_id = customer_id
        await db.commit()
    elif not existing:
        # Create subscription record with customer ID
        subscription = Subscription(
            user_id=current_user.id,
            status=SubscriptionStatus.PENDING.value,
            stripe_customer_id=customer_id,
        )
        db.add(subscription)
        await db.commit()

    # Build URLs
    success_url = (
        request.success_url
        or f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = request.cancel_url or f"{settings.FRONTEND_URL}/pricing"

    # Create checkout session
    result = stripe_service.create_checkout_session(
        user_id=str(current_user.id),
        customer_id=customer_id,
        price_id=price_id,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    logger.info(f"Created checkout session for user {current_user.id}, plan: {request.plan_type}")

    return CheckoutSessionResponse(
        session_id=result["session_id"],
        checkout_url=result["checkout_url"],
    )


@router.post(
    "/purchase-credits",
    response_model=CheckoutSessionResponse,
    summary="Create credit purchase checkout session",
)
async def purchase_credits(
    request: CreateCreditPurchaseRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout session for one-time credit purchase.

    Redirects user to Stripe's hosted checkout page to purchase credits.
    Credits are added to the user's account immediately after payment.
    Purchased credits never expire.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    # Check if price is configured for this pack
    price_id = stripe_service.get_credit_pack_price_id(request.credit_pack)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.PRICE_NOT_CONFIGURED, plan_type=request.credit_pack),
        )

    # Get or create Stripe customer
    customer_id = stripe_service.get_or_create_customer(
        user_id=str(current_user.id),
        email=current_user.email,
        name=current_user.full_name,
    )

    # Build URLs
    success_url = (
        request.success_url
        or f"{settings.FRONTEND_URL}/purchase/success?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = request.cancel_url or f"{settings.FRONTEND_URL}/pricing"

    # Create credit purchase checkout session
    result = stripe_service.create_credit_purchase_session(
        user_id=str(current_user.id),
        customer_id=customer_id,
        credit_pack=request.credit_pack,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    logger.info(
        f"Created credit purchase session for user {current_user.id}, pack: {request.credit_pack}"
    )

    return CheckoutSessionResponse(
        session_id=result["session_id"],
        checkout_url=result["checkout_url"],
    )


@router.post(
    "/create-portal-session",
    response_model=PortalSessionResponse,
    summary="Create customer portal session",
)
async def create_portal_session(
    request: CreatePortalSessionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PortalSessionResponse:
    """
    Create a Stripe Customer Portal session.

    Allows users to manage their subscription, update payment method, etc.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_user_id(current_user.id)

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.NO_BILLING_ACCOUNT),
        )

    return_url = request.return_url or f"{settings.FRONTEND_URL}/account"

    portal_url = stripe_service.create_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=return_url,
    )

    return PortalSessionResponse(portal_url=portal_url)


@router.get(
    "/subscription-status",
    response_model=SubscriptionStatusResponse,
    summary="Get subscription status",
)
async def get_subscription_status(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubscriptionStatusResponse:
    """
    Get current user's subscription status.
    """
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_user_id(current_user.id)

    if not subscription or not subscription.stripe_subscription_id:
        return SubscriptionStatusResponse(
            has_subscription=False,
            plan_type=PlanType.FREE.value,
        )

    # Calculate days until renewal
    days_until_renewal = None
    if subscription.current_period_end:
        delta = subscription.current_period_end - datetime.now(UTC)
        days_until_renewal = max(0, delta.days)

    return SubscriptionStatusResponse(
        has_subscription=True,
        plan_type=subscription.plan_type,
        status=subscription.status,
        stripe_subscription_id=subscription.stripe_subscription_id,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        days_until_renewal=days_until_renewal,
    )


@router.post(
    "/cancel-subscription",
    response_model=CancelSubscriptionResponse,
    summary="Cancel subscription",
)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CancelSubscriptionResponse:
    """
    Cancel current user's subscription.

    By default, cancels at end of billing period.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_user_id(current_user.id)

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.NO_SUBSCRIPTION_TO_CANCEL),
        )

    # Cancel via Stripe
    stripe_service.cancel_subscription(
        stripe_subscription_id=subscription.stripe_subscription_id,
        at_period_end=request.at_period_end,
    )

    # Update local record
    subscription.cancel_at_period_end = request.at_period_end
    subscription.updated_at = datetime.now(UTC)
    await db.commit()

    message = (
        _(StripeMessages.CANCELLED_AT_PERIOD_END)
        if request.at_period_end
        else _(StripeMessages.CANCELLED_IMMEDIATELY)
    )

    logger.info(
        f"User {current_user.id} cancelled subscription, at_period_end={request.at_period_end}"
    )

    return CancelSubscriptionResponse(
        success=True,
        message=message,
        cancel_at_period_end=request.at_period_end,
        current_period_end=subscription.current_period_end,
    )


@router.post(
    "/reactivate-subscription",
    response_model=CancelSubscriptionResponse,
    summary="Reactivate cancelled subscription",
)
async def reactivate_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CancelSubscriptionResponse:
    """
    Reactivate a subscription that was set to cancel at period end.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_user_id(current_user.id)

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.NO_SUBSCRIPTION_TO_REACTIVATE),
        )

    if not subscription.cancel_at_period_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.NOT_SCHEDULED_FOR_CANCELLATION),
        )

    # Reactivate via Stripe
    stripe_service.reactivate_subscription(
        stripe_subscription_id=subscription.stripe_subscription_id,
    )

    # Update local record
    subscription.cancel_at_period_end = False
    subscription.updated_at = datetime.now(UTC)
    await db.commit()

    logger.info(f"User {current_user.id} reactivated subscription")

    return CancelSubscriptionResponse(
        success=True,
        message=_(StripeMessages.SUBSCRIPTION_REACTIVATED),
        cancel_at_period_end=False,
        current_period_end=subscription.current_period_end,
    )


@router.get(
    "/payment-history",
    response_model=PaymentHistoryResponse,
    summary="Get payment history",
)
async def get_payment_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 20,
) -> PaymentHistoryResponse:
    """
    Get user's payment history.
    """
    payment_repo = PaymentRepository(db)
    offset = (page - 1) * page_size

    payments = await payment_repo.get_user_payments(
        user_id=current_user.id,
        limit=page_size + 1,  # Get one extra to check for more
        offset=offset,
    )

    has_more = len(payments) > page_size
    if has_more:
        payments = payments[:page_size]

    return PaymentHistoryResponse(
        payments=[PaymentRead.model_validate(p) for p in payments],
        total=len(payments),  # TODO: Add proper count query
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.post(
    "/webhooks",
    summary="Stripe webhook endpoint",
    include_in_schema=False,  # Hide from API docs
)
async def stripe_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    stripe_signature: Annotated[str, Header(alias="Stripe-Signature")],
):
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe and processes them.
    """
    if not stripe_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_(StripeMessages.NOT_CONFIGURED),
        )

    # Get raw body
    payload = await request.body()

    try:
        # Verify and construct event
        event = stripe_service.construct_webhook_event(payload, stripe_signature)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_(StripeMessages.INVALID_SIGNATURE),
        ) from e

    # Process the event
    try:
        result = await process_webhook_event(db, event)
        return result
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Return 200 to prevent Stripe from retrying
        # Error is logged and marked in webhook_events table
        return {"status": "error", "message": str(e)}
