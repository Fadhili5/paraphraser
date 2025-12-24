from app.users.model import UserModel
from datetime import datetime
import logging
import uuid
import asyncpg
from fastapi import HTTPException, status
from app.utils.token import create_access_token
from app.auth.password_handler import (
validate_password_strength, hash_password, verify_password
)

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_pool: asyncpg.pool.Pool):
        self.db_pool = db_pool

    """
    User service - Business Logic
    """
    # todo: Change phoneNumber Argument to lowercase
    async def register_user(self, email: str, password: str, phoneNumber: str, username: str):
        user_id = str(uuid.uuid4())[:8]
        hashed_password = hash_password(password)

        if not validate_password_strength(password):
            raise HTTPException(status_code=400, detail="Password is too weak!")

        async with self.db_pool.acquire() as conn:
            try:
                existing_user = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1 AND username = $2", email, username
                )

                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail="User with this email already exists!",
                    )

                row = await conn.fetchrow(
                    """
                    INSERT INTO users (id, username, email, password, phone, role)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    user_id, username, email, hashed_password, phoneNumber
                )

                return {
                    "message": "User Account successfully created!",
                    "user_id": row["id"]
                }

            except HTTPException:
                raise

            except Exception as e:
                logger.error(f"User Registration Request Error: Failed Registering a User: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User Registration Request Error"
                )

    async def get_user_by_email(self, email: str):
        async with self.db_pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1", email
                )

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User with this email does not exist!"
                    )

                return dict(user)
            except HTTPException:
                raise

            except Exception as e:
                logger.error(f"Get User Request: Failed executing the request: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Get User Request Error"
                )

    async def user_login(self, email: str, password: str):
        async with self.db_pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    "SELECT id, password FROM users WHERE email = $1",
                    email
                )

                if not user or not verify_password(password, user["password"]):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Credetials"
                    )

                token = create_access_token({"user_id": user["id"]})
                return {"access_token": token}

            except HTTPException:
                raise

            except Exception as e:
                logger.error(f"User Login Request Error: Failed Login: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User Login Request Error"
                )