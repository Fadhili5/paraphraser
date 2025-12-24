import uuid
import logging
from fastapi import HTTPException, status
import asyncpg

from app.users.dao import UserDAO
from app.auth.password_handler import (
    validate_password_strength,
    hash_password,
    verify_password,
)
from app.auth.jwt import create_access_token
from app.users.model import (UserRegisterResponse, TokenResponse)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_pool: asyncpg.pool.Pool):
        self.db_pool = db_pool

    async def register_user(self, email: str, password: str, phone_number: str, username: str):
        if not validate_password_strength(password):
            raise HTTPException(
                status_code=400,
                detail="Password is too weak"
            )

        user_id = str(uuid.uuid4())[:8]
        hashed_password = hash_password(password)

        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                dao = UserDAO(conn)

                existing = await dao.get_by_email_and_username(
                    email=email,
                    username=username
                )

                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail="User with this email or username already exists"
                    )

                created_id = await dao.create_user(
                    user_id=user_id,
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    phone=phone_number
                )

                return UserRegisterResponse(
                    message="User Account successfully created!",
                    user_id=created_id
                )

    async def user_login(self, email: str, password: str):
        async with self.db_pool.acquire() as conn:
            dao = UserDAO(conn)

            user = await dao.get_by_email(email)

            if not user or not verify_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            token = create_access_token({"user_id": user.id})

            return TokenResponse(access_token=token)
