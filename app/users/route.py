from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status

from app.models import ForgotPasswordRequest, ResetPasswordRequest
from app.users.service import UserService
from app.users.dao import UserDAO
import asyncpg
from app.users.model import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, TokenResponse
from app.db.connection import get_pool
from app.core.rate_limit import rate_limit
from app.auth.recaptcha import guard_captcha
from app.auth.googleoauth import verify_google_token
from pydantic import BaseModel

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
@rate_limit()
async def register_user(request: Request, payload: UserRegisterRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    guard_captcha(token=payload.recaptcha_token, expected_action="register", min_score=0.5)
    async with db_pool.acquire() as conn:
        user_dao = UserDAO(conn)
        service = UserService(user_dao)
        return await service.register_user(
            email=payload.email,
            username=payload.username,
            password=payload.password,
            phone_number=payload.phone_number,
        )

@router.post("/login", response_model=TokenResponse)
@rate_limit(limit=5, window=60)
async def user_login(request: Request, payload: UserLoginRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    guard_captcha(token=payload.recaptcha_token, expected_action="login", min_score=0.5)
    async with db_pool.acquire() as conn:
        user_dao = UserDAO(conn)
        service = UserService(user_dao)
        return await service.user_login(
            email=payload.email,
            password=payload.password
        )

# New Features: Google's OAuth2.0 Verification for Login & Password Reset Request For Forgotten Passwords
class GoogleAuthRequest(BaseModel):
    token: str

@router.post("/google-signin")
async def google_login(payload: GoogleAuthRequest):
    user = verify_google_token(payload.token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {
        "message": "Authenticated",
        "user": user
    }

@router.post("/forgot_password")
@rate_limit(limit=5, window=60)
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    guard_captcha(
        token=payload.recaptcha_token,
        expected_action="forgot_password",
        min_score=0.5
    )
    async with db_pool.acquire() as conn:
        user_dao = UserDAO(conn)
        service = UserService(user_dao)

        return await service.forgot_password(email=payload.email)

@router.post("/reset_password")
@rate_limit(limit=5, window=60)
async def reset_password(request: Request, payload: ResetPasswordRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    async with db_pool.acquire() as conn:
        user_dao = UserDAO(conn)
        service = UserService(user_dao)

        return await service.reset_password(
            token=payload.token,
            new_password=payload.new_password
        )