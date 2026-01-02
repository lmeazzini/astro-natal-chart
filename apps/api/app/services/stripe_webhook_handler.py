"""Stripe webhook event handlers."""

from datetime import UTC, datetime
from uuid import UUID

import stripe
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PlanType, SubscriptionChangeType, SubscriptionStatus, UserRole
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.subscription_history import SubscriptionHistory
from app.models.webhook_event import WebhookEvent
from app.repositories.audit_repository import AuditRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.subscription_history_repository import SubscriptionHistoryRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.webhook_event_repository import WebhookEventRepository
from app.services.amplitude_service import amplitude_service
from app.services.credit_service import allocate_credits
from app.services.stripe_service import stripe_service


async def _record_webhook_event(
    db: AsyncSession,
    event: stripe.Event,
    status: str = "pending",
) -> WebhookEvent:
    """Record a webhook event for idempotency tracking."""
    webhook_repo = WebhookEventRepository(db)

    webhook_event = WebhookEvent(
        stripe_event_id=event.id,
        event_type=event.type,
        status=status,
        payload=event.to_dict(),
    )
    return await webhook_repo.create(webhook_event)


async def _create_subscription_history(
    db: AsyncSession,
    subscription: Subscription,
    change_type: SubscriptionChangeType,
    change_reason: str | None = None,
) -> SubscriptionHistory:
    """Create subscription history record."""
    history_repo = SubscriptionHistoryRepository(db)
    history = SubscriptionHistory(
        subscription_id=subscription.id,
        user_id=subscription.user_id,
        status=subscription.status,
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
        change_type=change_type.value,
        changed_by_user_id=None,  # Stripe system change
        change_reason=change_reason,
    )
    return await history_repo.create(history)


async def handle_checkout_session_completed(
    db: AsyncSession,
    event: stripe.Event,
) -> None:
    """
    Handle checkout.session.completed event.

    Creates or updates subscription when a checkout is completed.
    """
    session = event.data.object
    user_id_str = session.metadata.get("user_id")

    if not user_id_str:
        logger.error(f"checkout.session.completed missing user_id in metadata: {session.id}")
        return

    user_id = UUID(user_id_str)
    user_repo = UserRepository(db)
    subscription_repo = SubscriptionRepository(db)
    audit_repo = AuditRepository(db)

    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.error(f"User not found for checkout session: {user_id}")
        return

    # Get subscription from Stripe
    stripe_subscription = stripe.Subscription.retrieve(session.subscription)
    price_id = stripe_subscription["items"]["data"][0]["price"]["id"]
    plan_type = stripe_service.get_plan_for_price_id(price_id)

    # Get or create subscription record
    subscription = await subscription_repo.get_by_user_id(user_id)
    now = datetime.now(UTC)

    if subscription:
        # Update existing subscription
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.plan_type = plan_type
        subscription.stripe_customer_id = session.customer
        subscription.stripe_subscription_id = stripe_subscription.id
        subscription.stripe_price_id = price_id
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start, tz=UTC
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end, tz=UTC
        )
        subscription.cancel_at_period_end = False
        subscription.updated_at = now
    else:
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            status=SubscriptionStatus.ACTIVE.value,
            plan_type=plan_type,
            stripe_customer_id=session.customer,
            stripe_subscription_id=stripe_subscription.id,
            stripe_price_id=price_id,
            started_at=now,
            current_period_start=datetime.fromtimestamp(
                stripe_subscription.current_period_start, tz=UTC
            ),
            current_period_end=datetime.fromtimestamp(
                stripe_subscription.current_period_end, tz=UTC
            ),
        )
        subscription = await subscription_repo.create(subscription)

    # Update user role to PREMIUM
    user.role = UserRole.PREMIUM.value

    # Allocate credits for the new plan
    await allocate_credits(db, user_id, plan_type)

    # Create audit log
    await audit_repo.create_log(
        user_id=user_id,
        action="subscription_created",
        resource_type="subscription",
        resource_id=subscription.id,
        extra_data={
            "stripe_subscription_id": stripe_subscription.id,
            "plan_type": plan_type,
            "source": "stripe_checkout",
        },
    )

    # Create history record
    await _create_subscription_history(
        db, subscription, SubscriptionChangeType.GRANTED, "Stripe checkout completed"
    )

    await db.commit()

    # Track with Amplitude
    amplitude_service.track(
        event_type="subscription_created",
        user_id=str(user_id),
        event_properties={
            "plan_type": plan_type,
            "stripe_subscription_id": stripe_subscription.id,
            "source": "stripe_checkout",
        },
    )

    logger.info(f"Subscription created for user {user_id}, plan: {plan_type}")


async def handle_subscription_updated(
    db: AsyncSession,
    event: stripe.Event,
) -> None:
    """
    Handle customer.subscription.updated event.

    Updates subscription status, dates, and handles plan changes.
    """
    stripe_subscription = event.data.object
    subscription_repo = SubscriptionRepository(db)

    subscription = await subscription_repo.get_by_stripe_subscription_id(stripe_subscription.id)
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {stripe_subscription.id}")
        return

    # Get price and plan type
    price_id = stripe_subscription["items"]["data"][0]["price"]["id"]
    new_plan_type = stripe_service.get_plan_for_price_id(price_id)
    old_plan_type = subscription.plan_type

    # Update subscription
    subscription.status = SubscriptionStatus.ACTIVE.value
    subscription.stripe_price_id = price_id
    subscription.plan_type = new_plan_type
    subscription.current_period_start = datetime.fromtimestamp(
        stripe_subscription.current_period_start, tz=UTC
    )
    subscription.current_period_end = datetime.fromtimestamp(
        stripe_subscription.current_period_end, tz=UTC
    )
    subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end
    subscription.updated_at = datetime.now(UTC)

    # If plan changed, update credits
    if old_plan_type != new_plan_type:
        await allocate_credits(db, subscription.user_id, new_plan_type)
        change_reason = f"Plan changed from {old_plan_type} to {new_plan_type}"
    else:
        change_reason = "Subscription updated"

    # Create history record
    await _create_subscription_history(
        db, subscription, SubscriptionChangeType.EXTENDED, change_reason
    )

    await db.commit()

    # Track plan change
    if old_plan_type != new_plan_type:
        amplitude_service.track(
            event_type="subscription_plan_changed",
            user_id=str(subscription.user_id),
            event_properties={
                "old_plan_type": old_plan_type,
                "new_plan_type": new_plan_type,
                "source": "stripe_webhook",
            },
        )

    logger.info(f"Subscription updated: {stripe_subscription.id}")


async def handle_subscription_deleted(
    db: AsyncSession,
    event: stripe.Event,
) -> None:
    """
    Handle customer.subscription.deleted event.

    Cancels subscription and downgrades user to free tier.
    """
    stripe_subscription = event.data.object
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    subscription = await subscription_repo.get_by_stripe_subscription_id(stripe_subscription.id)
    if not subscription:
        logger.warning(f"Subscription not found for deletion: {stripe_subscription.id}")
        return

    # Update subscription status
    subscription.status = SubscriptionStatus.CANCELLED.value
    subscription.updated_at = datetime.now(UTC)

    # Downgrade user to FREE
    user = await user_repo.get_by_id(subscription.user_id)
    if user:
        user.role = UserRole.FREE.value

    # Reset credits to free tier
    await allocate_credits(db, subscription.user_id, PlanType.FREE.value)

    # Create audit log
    await audit_repo.create_log(
        user_id=subscription.user_id,
        action="subscription_cancelled",
        resource_type="subscription",
        resource_id=subscription.id,
        extra_data={
            "stripe_subscription_id": stripe_subscription.id,
            "source": "stripe_webhook",
        },
    )

    # Create history record
    await _create_subscription_history(
        db, subscription, SubscriptionChangeType.REVOKED, "Subscription cancelled via Stripe"
    )

    await db.commit()

    # Track with Amplitude
    amplitude_service.track(
        event_type="subscription_cancelled",
        user_id=str(subscription.user_id),
        event_properties={
            "stripe_subscription_id": stripe_subscription.id,
            "source": "stripe_webhook",
        },
    )

    logger.info(f"Subscription cancelled: {stripe_subscription.id}")


async def handle_invoice_payment_succeeded(
    db: AsyncSession,
    event: stripe.Event,
) -> None:
    """
    Handle invoice.payment_succeeded event.

    Records payment and resets credits for the new billing period.
    """
    invoice = event.data.object

    # Skip if no subscription (one-time payment)
    if not invoice.subscription:
        return

    subscription_repo = SubscriptionRepository(db)
    payment_repo = PaymentRepository(db)

    subscription = await subscription_repo.get_by_stripe_subscription_id(invoice.subscription)
    if not subscription:
        logger.warning(f"Subscription not found for invoice: {invoice.subscription}")
        return

    # Check if payment already recorded (idempotency)
    existing_payment = await payment_repo.get_by_stripe_invoice(invoice.id)
    if existing_payment:
        logger.info(f"Payment already recorded for invoice: {invoice.id}")
        return

    # Record payment
    payment = Payment(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        stripe_invoice_id=invoice.id,
        stripe_payment_intent_id=invoice.payment_intent,
        amount=invoice.amount_paid,
        currency=invoice.currency,
        status="succeeded",
        receipt_url=invoice.hosted_invoice_url,
        description=f"Subscription payment - {subscription.plan_type}",
    )
    await payment_repo.create(payment)

    # Reset credits for new billing period (monthly renewal)
    # Only reset if this is a renewal (not the first payment)
    if invoice.billing_reason == "subscription_cycle":
        from app.services.credit_service import reset_monthly_credits

        await reset_monthly_credits(db, subscription.user_id)

    await db.commit()

    # Track with Amplitude
    amplitude_service.track(
        event_type="payment_succeeded",
        user_id=str(subscription.user_id),
        event_properties={
            "amount": invoice.amount_paid,
            "currency": invoice.currency,
            "plan_type": subscription.plan_type,
            "source": "stripe_webhook",
        },
    )

    logger.info(
        f"Payment recorded for user {subscription.user_id}: {invoice.amount_paid} {invoice.currency}"
    )


async def handle_invoice_payment_failed(
    db: AsyncSession,
    event: stripe.Event,
) -> None:
    """
    Handle invoice.payment_failed event.

    Records failed payment and can trigger notifications.
    """
    invoice = event.data.object

    if not invoice.subscription:
        return

    subscription_repo = SubscriptionRepository(db)
    payment_repo = PaymentRepository(db)

    subscription = await subscription_repo.get_by_stripe_subscription_id(invoice.subscription)
    if not subscription:
        return

    # Record failed payment
    payment = Payment(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        stripe_invoice_id=invoice.id,
        stripe_payment_intent_id=invoice.payment_intent,
        amount=invoice.amount_due,
        currency=invoice.currency,
        status="failed",
        description=f"Failed payment - {subscription.plan_type}",
    )
    await payment_repo.create(payment)

    await db.commit()

    # Track with Amplitude
    amplitude_service.track(
        event_type="payment_failed",
        user_id=str(subscription.user_id),
        event_properties={
            "amount": invoice.amount_due,
            "currency": invoice.currency,
            "plan_type": subscription.plan_type,
            "attempt_count": invoice.attempt_count,
            "source": "stripe_webhook",
        },
    )

    logger.warning(f"Payment failed for user {subscription.user_id}: {invoice.id}")

    # TODO: Send email notification to user about failed payment


async def process_webhook_event(
    db: AsyncSession,
    event: stripe.Event,
) -> dict:
    """
    Process a Stripe webhook event with idempotency.

    Args:
        db: Database session
        event: Stripe event object

    Returns:
        Dict with processing result
    """
    webhook_repo = WebhookEventRepository(db)

    # Check idempotency - skip if already processed
    if await webhook_repo.event_already_processed(event.id):
        logger.info(f"Webhook event already processed: {event.id}")
        return {"status": "skipped", "message": "Event already processed"}

    # Record event
    await _record_webhook_event(db, event)

    try:
        # Route to appropriate handler
        handlers = {
            "checkout.session.completed": handle_checkout_session_completed,
            "customer.subscription.updated": handle_subscription_updated,
            "customer.subscription.deleted": handle_subscription_deleted,
            "invoice.payment_succeeded": handle_invoice_payment_succeeded,
            "invoice.payment_failed": handle_invoice_payment_failed,
        }

        handler = handlers.get(event.type)
        if handler:
            await handler(db, event)
            await webhook_repo.mark_as_processed(event.id)
            logger.info(f"Processed webhook event: {event.type} ({event.id})")
            return {"status": "processed", "event_type": event.type}
        else:
            # Unknown event type - mark as processed to avoid retries
            await webhook_repo.mark_as_processed(event.id)
            logger.debug(f"Unhandled webhook event type: {event.type}")
            return {"status": "ignored", "event_type": event.type}

    except Exception as e:
        # Mark as failed
        await webhook_repo.mark_as_failed(event.id, str(e))
        await db.commit()
        logger.error(f"Webhook processing failed: {event.type} - {e}")
        raise
