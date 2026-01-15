from datetime import timedelta, datetime

import jwt
import os
import dotenv
from dotenv import load_dotenv
from fastapi import Request, HTTPException, Depends
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(subject: dict, expires_delta: timedelta = timedelta(minutes=5)):
    to_encode = subject.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # e.g. {'id': 1, 'username': 'john', 'role': 'farmer'}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

def require_role(role: str):
    async def role_dependency(user=Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    return role_dependency

def verify_jwt_token(token: str) -> dict | None:
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except ExpiredSignatureError:
        print("Token has expired")
        return None
    except InvalidTokenError:
        print("Invalid Token")
        return None

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None