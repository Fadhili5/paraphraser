import os
import requests
from fastapi import HTTPException
from starlette import status

def guard_captcha(token: str, expected_action: str, min_score: float = 0.5):
    secret = os.getenv("RECAPTCHA_SECRET")

    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Captcha service not configured",
        )

    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": secret,
                "response": token,
            },
            timeout=5,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="reCAPTCHA verification services are currently unavailable",
        )

    result = response.json()

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="reCAPTCHA verification failed",
        )

    action = result.get("action")
    score = result.get("score", 0.0)

    if action != expected_action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reCAPTCHA action: {action}",
        )

    if score < min_score:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bot detected",
        )

    return {
        "score": score,
        "action": action,
    }