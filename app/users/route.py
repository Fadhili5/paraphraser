from fastapi import APIRouter, Depends
from app.users.service import UserService
import asyncpg
from app.users.model import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, TokenResponse
from app.db.connection import get_pool

router = APIRouter(prefix="/v1/users", tags=["Users"])

# Use some dependency injection
@router.post("/register", response_model=UserRegisterResponse, status_code=201)
async def register_user(payload: UserRegisterRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    service = UserService(db_pool)

    return await service.register_user(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        phone_number=payload.phone_number,
    )

@router.post("/login", response_model=TokenResponse)
async def user_login(payload: UserLoginRequest, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    service = UserService(db_pool)

    return await service.user_login(
        email=payload.email,
        password=payload.password
    )