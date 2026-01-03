"""Stripe payment service for subscription management."""

from typing import Any

import stripe
from loguru import logger

from app.core.config import settings
from app.models.enums import PlanType

# Configure Stripe with API key
if settings.stripe_enabled:
    stripe.api_key = settings.STRIPE_SECRET_KEY


# Map plan types to Stripe price IDs
PLAN_PRICE_MAP: dict[str, str | None] = {
    PlanType.STARTER.value: settings.STRIPE_PRICE_STARTER,
    PlanType.PRO.value: settings.STRIPE_PRICE_PRO,
    PlanType.UNLIMITED.value: settings.STRIPE_PRICE_UNLIMITED,
}

# Map Stripe price IDs back to plan types
PRICE_PLAN_MAP: dict[str, str] = {}
if settings.STRIPE_PRICE_STARTER:
    PRICE_PLAN_MAP[settings.STRIPE_PRICE_STARTER] = PlanType.STARTER.value
if settings.STRIPE_PRICE_PRO:
    PRICE_PLAN_MAP[settings.STRIPE_PRICE_PRO] = PlanType.PRO.value
if settings.STRIPE_PRICE_UNLIMITED:
    PRICE_PLAN_MAP[settings.STRIPE_PRICE_UNLIMITED] = PlanType.UNLIMITED.value


class StripeService:
    """Service for Stripe payment operations."""

    @property
    def enabled(self) -> bool:
        """Check if Stripe is properly configured."""
        return settings.stripe_enabled

    def get_or_create_customer(
        self,
        user_id: str,
        email: str,
        name: str | None = None,
    ) -> str:
        """
        Get existing Stripe customer or create a new one.

        Args:
            user_id: Internal user ID (stored as metadata)
            email: Customer email
            name: Customer name (optional)

        Returns:
            Stripe customer ID
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        # Search for existing customer by email
        existing_customers = stripe.Customer.search(
            query=f"email:'{email}'",
            limit=1,
        )

        if existing_customers.data:
            customer = existing_customers.data[0]
            logger.info(f"Found existing Stripe customer: {customer.id}")
            return customer.id

        # Create new customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": user_id},
        )
        logger.info(f"Created new Stripe customer: {customer.id}")
        return customer.id

    def create_checkout_session(
        self,
        user_id: str,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> dict[str, str]:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            user_id: Internal user ID
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the plan
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled

        Returns:
            Dict with session_id and checkout_url
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id},
            subscription_data={
                "metadata": {"user_id": user_id},
            },
            # Payment method configuration
            payment_method_types=["card"],
            # Allow promotion codes
            allow_promotion_codes=True,
            # Billing address collection
            billing_address_collection="auto",
            # Customer update settings
            customer_update={
                "address": "auto",
                "name": "auto",
            },
        )

        logger.info(f"Created Stripe checkout session: {session.id} for user {user_id}")
        return {
            "session_id": session.id,
            "checkout_url": session.url or "",
        }

    def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """
        Create a Stripe Customer Portal session.

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session

        Returns:
            Portal session URL
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        logger.info(f"Created Stripe portal session for customer: {customer_id}")
        return session.url

    def cancel_subscription(
        self,
        stripe_subscription_id: str,
        at_period_end: bool = True,
    ) -> stripe.Subscription:
        """
        Cancel a Stripe subscription.

        Args:
            stripe_subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of billing period (default)

        Returns:
            Updated Stripe subscription object
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        if at_period_end:
            # Cancel at the end of the billing period
            subscription = stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=True,
            )
            logger.info(f"Subscription {stripe_subscription_id} set to cancel at period end")
        else:
            # Cancel immediately
            subscription = stripe.Subscription.cancel(stripe_subscription_id)
            logger.info(f"Subscription {stripe_subscription_id} cancelled immediately")

        return subscription

    def reactivate_subscription(
        self,
        stripe_subscription_id: str,
    ) -> stripe.Subscription:
        """
        Reactivate a subscription that was set to cancel at period end.

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Updated Stripe subscription object
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=False,
        )
        logger.info(f"Subscription {stripe_subscription_id} reactivated")
        return subscription

    def get_subscription(
        self,
        stripe_subscription_id: str,
    ) -> stripe.Subscription:
        """
        Retrieve a Stripe subscription.

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Stripe subscription object
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        return stripe.Subscription.retrieve(stripe_subscription_id)

    def construct_webhook_event(
        self,
        payload: bytes,
        signature: str,
    ) -> stripe.Event:
        """
        Construct and verify a Stripe webhook event.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header value

        Returns:
            Verified Stripe event object

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    def get_price_id_for_plan(self, plan_type: str) -> str | None:
        """
        Get Stripe price ID for a plan type.

        Args:
            plan_type: Plan type (starter, pro, unlimited)

        Returns:
            Stripe price ID or None if not configured
        """
        return PLAN_PRICE_MAP.get(plan_type)

    def get_plan_for_price_id(self, price_id: str) -> str:
        """
        Get plan type for a Stripe price ID.

        Args:
            price_id: Stripe price ID

        Returns:
            Plan type string (defaults to 'free' if not found)
        """
        return PRICE_PLAN_MAP.get(price_id, PlanType.FREE.value)

    def get_invoice(self, invoice_id: str) -> stripe.Invoice:
        """
        Retrieve a Stripe invoice.

        Args:
            invoice_id: Stripe invoice ID

        Returns:
            Stripe invoice object
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        return stripe.Invoice.retrieve(invoice_id)

    def get_payment_intent(self, payment_intent_id: str) -> stripe.PaymentIntent:
        """
        Retrieve a Stripe payment intent.

        Args:
            payment_intent_id: Stripe payment intent ID

        Returns:
            Stripe payment intent object
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        return stripe.PaymentIntent.retrieve(payment_intent_id)

    def create_subscription_preview(
        self,
        customer_id: str,
        price_id: str,
    ) -> dict[str, Any]:
        """
        Create a preview of subscription pricing.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID

        Returns:
            Dict with pricing preview details
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not configured")

        # Create an invoice preview
        invoice = stripe.Invoice.create_preview(
            customer=customer_id,
            subscription_items=[{"price": price_id}],
        )

        return {
            "amount_due": invoice.amount_due,
            "currency": invoice.currency,
            "period_start": invoice.period_start,
            "period_end": invoice.period_end,
        }


# Singleton instance
stripe_service = StripeService()
