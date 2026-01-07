from fastapi import Depends, HTTPException, status
from app.billing.plans import PLAN_LIMITS
from app.auth.guard import paid_user


def usage_guard(characters_needed: int):
    async def _guard(user=Depends(paid_user)):
        plan = user.plan
        limit = PLAN_LIMITS.get(plan)

        if limit is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown subscription plan",
            )

        if user.monthly_characters_used + characters_needed > limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly usage limit exceeded",
            )

        return user

    return _guard
