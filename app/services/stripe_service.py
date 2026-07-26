import stripe
from decimal import Decimal
from app.core.config import settings
from app.core.logger import logger

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    
    @staticmethod
    def create_checkout_session(
        order_id: str,
        amount: Decimal,
        currency: str,
        customer_email: str | None,
        success_url: str,
        cancel_url: str
    ) -> stripe.checkout.Session:
        """
        Creates a Stripe Checkout Session for a given order amount.
        Stripe amounts are calculated in cents (e.g. $10.50 -> 1050).
        """
        amount_in_cents = int(amount * 100)

        session_payload = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {
                            "name": f"Restaurant Order #{order_id[:8]}",
                            "description": f"Payment for FastTable Order ID: {order_id}",
                        },
                        "unit_amount": amount_in_cents,
                    },
                    "quantity": 1,
                }
            ],
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "order_id": order_id
            }
        }

        if customer_email:
            session_payload["customer_email"] = customer_email

        logger.info(f"Creating Stripe Checkout Session for Order ID: {order_id}")
        return stripe.checkout.Session.create(**session_payload)

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """
        Verifies the cryptographic signature of incoming Stripe Webhook events.
        """
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )

stripe_service = StripeService()
