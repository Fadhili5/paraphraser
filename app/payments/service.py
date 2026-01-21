import stripe
from app.config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

FRONTEND_URL = f"http://localhost:8000"

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
STRIPE_PRICE_PLAN = {
    "basic": "",
    "pro": ""
}

def create_checkout_session(*, amount: int, user_id: str, plan: str, customer_id: str | None = None):
    if plan not in STRIPE_PRICE_PLAN:
        raise ValueError(f"Invalid plan {plan}")

    session = stripe.checkout.Session.create(
        mode="Subscription",
        customer_id=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": STRIPE_PRICE_PLAN[plan],
                "quantity": 1,
            }
        ],
        metadata={
            "user_id": user_id,
            "plan": plan,
        },
        success_url=f"{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/billing/cancel"
    )
    return session