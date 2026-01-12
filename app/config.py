import os

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or STRIPE_WEBHOOK_SECRET:
    raise RuntimeError("Stripe Env Variables Are Missing")