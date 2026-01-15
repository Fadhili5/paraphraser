import os

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

# Only validate in production
if os.getenv("ENV") == "production":
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("Stripe Env Variables Are Missing")