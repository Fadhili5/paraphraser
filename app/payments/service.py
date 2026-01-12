import stripe
from app.config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

def create_payment_intent(*, amount: int, currency: str, order_id: str, customer_email: str | None = None):
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        automatic_payment_methods={"enabled": True},
        metadata={
            "order_id": order_id
        },
        receipt_email=customer_email,
    )

    return intent