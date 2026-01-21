from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.payments.service import create_checkout_session
from app.db.connection import get_pool
import stripe


from app.payments.service import create_payment_intent

router = APIRouter(prefix="/payments", tags=["payments"])

class CreatePaymentRequest(BaseModel):
    amount: int
    currency: str
    order_id: str
    email: str | None = None

@router.post("/create")
def create_payment(req: CreatePaymentRequest):
    try:
        intent = create_payment_intent(
            amount=req.amount,
            currency=req.currency,
            order_id=req.order_id,
            customer_email=req.email,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "client_secret": intent.client_secret
    }

FRONTEND_URL = "https://paraphraze.tech"

@router.post("/stripe/checkout-session")
async def checkout_session_router(user_id: str, plan: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            """
            SELECT id, email, stripe_customer_id
            FROM users
            WHERE id = $1
            """,
            user_id,
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        stripe_customer_id = user["stripe_customer_id"]

        # Create Stripe customer if missing
        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=user["email"],
                metadata={"user_id": user_id},
            )

            stripe_customer_id = customer.id

            await conn.execute(
                """
                UPDATE users
                SET stripe_customer_id = $1
                WHERE id = $2
                """,
                stripe_customer_id,
                user_id,
            )

    try:
        session = create_checkout_session(
            customer_id=stripe_customer_id,
            user_id=user_id,
            plan=plan,
            frontend_url=FRONTEND_URL,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "checkout_url": session.url
    }
