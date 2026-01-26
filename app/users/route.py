from fastapi import APIRouter, Depends, Request
from app.users.service import UserService
from app.users.dao import UserDAO
import asyncpg
from app.users.model import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, TokenResponse
from app.db.connection import get_pool
from app.core.rate_limit import rate_limit
from app.auth.recaptcha import guard_captcha

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
@rate_limit(limit=5, window=60)
async def register_user(request: Request, payload: UserRegisterRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    guard_captcha(token=payload.recaptcha_token, expected_action="register", min_score=0.5)
    async with db_pool.acquire() as conn:
        user_dao = UserDAO(conn)
        service = UserService(user_dao)
        return await service.register_user(
            email=payload.email,
            username=payload.username,
            password=payload.password,
            phone=payload.phone_number,
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
