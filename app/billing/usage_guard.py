from fastapi import Depends, HTTPException, status
from app.billing.plans import PLAN_LIMITS
from app.auth.guard import paid_user


def usage_guard(characters_needed: int):
    async def _guard(user=Depends(paid_user)):
        plan = user.plan
        config = PLAN_LIMITS.get(plan)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Plan: {plan} not available"
            )

        # A monthly limit
        if user.monthly_characters_used + characters_needed > config["max_characters"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly usage limit exceeded"
            )

        # Per request limit
        if characters_needed > config["max_chars_per_request"]:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Request too large for your plan"
            )
        return user
    return _guard