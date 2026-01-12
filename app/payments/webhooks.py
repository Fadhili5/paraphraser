from fastapi import APIRouter, Request, Header, HTTPException
import stripe

from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.db.connection import get_pool

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=stripe_signature, secret=STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    pool = await get_pool()
    event_type = event["type"]
    data = event["data"]["object"]

    # Successful Payments
    if event_type == "payment_intent.succeeded":
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        plan = metadata.get("plan")

        if not user_id or not plan:
            return {"status": "missing_metadata"}

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users
                SET plan = $1,
                    subscription_status = 'active'
                WHERE id = $2
                """,
                plan,
                user_id,
            )

        return {"status": "upgraded"}

    # Downgrade User's Accounts on Failure
    if event_type in {
        "payment_intent.payment_failed",
        "invoice.payment_failed",
        "customer.subscription.deleted",
    }:
        user_id = None

        metadata = data.get("metadata")
        if metadata:
            user_id = metadata.get("user_id")

        async with pool.acquire() as conn:
            # Fallback via Stripe customer ID
            if not user_id and data.get("customer"):
                row = await conn.fetchrow(
                    """
                    SELECT id
                    FROM users
                    WHERE stripe_customer_id = $1
                    """,
                    data["customer"],
                )
                if row:
                    user_id = row["id"]

            if not user_id:
                return {"status": "user_not_found"}

            await conn.execute(
                """
                UPDATE users
                SET plan = 'free',
                    subscription_status = 'inactive'
                WHERE id = $1
                """,
                user_id,
            )

        return {"status": "downgraded"}

    return {"status": "ignored"}
