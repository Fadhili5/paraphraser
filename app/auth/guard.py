from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user


async def verified_user(user=Depends(get_current_user)):
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified",
        )
    return user

async def paid_user(user=Depends(verified_user)):
    if not user.has_active_subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required",
        )
    return user
