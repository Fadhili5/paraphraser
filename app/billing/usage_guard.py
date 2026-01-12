from fastapi import Depends, HTTPException, status
from app.billing.plans import PLAN_LIMITS
from app.auth.guard import paid_user


def usage_guard(characters_needed: int):
    async def _guard(user=Depends(paid_user)):
        plan = user.plan
        plan_config = PLAN_LIMITS.get(plan)

        if not plan_config:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown subscription plan",
            )

        max_chars = plan_config["max_characters"]

        if user.monthly_characters_used + characters_needed > max_chars:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly usage limit exceeded",
            )

        return user

    return _guard
