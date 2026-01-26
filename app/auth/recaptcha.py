import os
import requests
from fastapi import HTTPException
from starlette import status

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")

if not RECAPTCHA_SECRET:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Captcha service not configured"
    )
    #raise RuntimeError("RECAPTCHA_SECRET not set")

def guard_captcha(token: str, expected_action: str, min_score: float = 0.5):
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET,
                "response": token,
            },
            timeout=5,
        )
    except requests.RequestException:
        # This is for when Google is unavailable
        raise HTTPException(
            status_code=503,
            detail=f"reCAPTCHA verification services are currently unavailable"
        )
    result = response.json()

    if not result.get("success"):
        raise HTTPException(
            status_code=403,
            detail=f"reCAPTCHA verification failed"
        )

    # reCAPTCHA v3 specific checks
    action = result.get("action")
    score = result.get("score", 0.0)

    if action != expected_action:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reCAPTCHA action: {action}"
        )

    if score < min_score:
        raise HTTPException(
            status_code=403,
            detail=f"Bot Detected"
        )
    return  {
        "score": score,
        "action": action
    }