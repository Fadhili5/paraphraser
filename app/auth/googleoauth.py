import os
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

def verify_google_token(token: str) -> dict | None:
    if not settings.GOOGLE_CLIENT_ID:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return {
            "google_id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name")
        }
    except Exception:
        return None