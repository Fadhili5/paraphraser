import uuid
import logging
from fastapi import HTTPException, status

from app.users.dao import UserDAO
from app.auth.password_handler import (validate_password_strength, hash_password, verify_password)
from app.auth.jwt import create_access_token
from app.users.model import UserRegisterResponse, TokenResponse

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, dao: UserDAO | None = None, db_pool=None):
        if dao is not None:
            self.dao = dao
        elif db_pool is not None:
            self.dao = UserDAO(db_pool)
        else:
            raise ValueError("UserService requires either dao or db_pool")

    async def register_user(self, email: str, password: str, phone: str, username: str):
        # 1. Password validation with proper error propagation
        try:
            validate_password_strength(password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # 2. Check for existing user
        existing = await self.dao.get_by_email_and_username(
            email=email,
            username=username,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        # 3. Create user
        user_id = str(uuid.uuid4())[:8]
        hashed_password = hash_password(password)

        created_id = await self.dao.create_user(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            phone=phone,
        )

        return UserRegisterResponse(
            message="User Account successfully created!",
            user_id=created_id,
        )

    async def user_login(self, email: str, password: str):
        user = await self.dao.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token = create_access_token({"user_id": user.id})

        return TokenResponse(access_token=token)
