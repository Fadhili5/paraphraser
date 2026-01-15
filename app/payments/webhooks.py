import json
from fastapi import APIRouter, Request, Header, HTTPException
import stripe
from fastapi.responses import JSONResponse

from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.db.connection import get_pool

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = STRIPE_SECRET_KEY
webhook_secret = STRIPE_WEBHOOK_SECRET


@router.post("/stripe/webhook")
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

# Add a Subscription Web-Hook
@router.post("/stripe/webhook")
async def webhook_received(request: Request, stripe_signature: str | None = Header(default=None, alias="Stripe-Signature")):
    payload = await request.body()
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=stripe_signature,
                secret=webhook_secret,
            )
        else:
            event = json.loads(payload)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    event_type = event["type"]
    data_object = event["data"]["object"]
    print(f"event {event_type}")

    if event_type == "checkout.session.completed":
        print("Payment Succeeded")
    elif event_type == "customer.subscription.trial_will_end":
        print("Subscription trial will end")
    elif event_type == "customer.subscription.created":
        print(f"Subscription Created: {event['id']}")
    elif event_type == "customer.subscription.updated":
        print(f"Subscription Updated: {event['id']}")
    elif event_type == "customer.subscription.deleted":
        print(f"Subscription Deleted: {event['id']}")
    elif event_type == "entitlements.active_entitlement_summary.updated":
        print(f"Active entitlement summary updated {event['id']}")

    return JSONResponse({"status": "success"})


"""todo: Implement webhooks and auditability
setup webhooks for invoice.paid, invoice.payment_failed, customer_subscription.updated, charge.refunded"""