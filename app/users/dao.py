from typing import Optional
import asyncpg
import uuid
from app.users.model import UserDB
from datetime import datetime, timedelta


class UserDAO:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_by_email(self, email: str) -> Optional[UserDB]:
        row = await self.conn.fetchrow(
            """
            SELECT id, username, email, password, phone_number, role
            FROM users
            WHERE email = $1
            """,
            email,
        )
        return UserDB(**dict(row)) if row else None

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[UserDB]:
        row = await self.conn.fetchrow(
            """
            SELECT id, username, email, phone_number, role
            FROM users
            WHERE id = $1
            """,
            user_id,
        )
        return UserDB(**dict(row)) if row else None

    async def get_by_email_and_username(self, email: str, username: str) -> Optional[UserDB]:
        row = await self.conn.fetchrow(
            """
            SELECT id, username, email, phone_number, role
            FROM users
            WHERE email = $1 OR username = $2
            """,
            email,
            username,
        )
        return UserDB(**dict(row)) if row else None

    async def create_user(self, user_id: str, username: str, email: str, hashed_password: str, phone_number: str, role: str = "user") -> str:
        row = await self.conn.fetchrow(
            """
            INSERT INTO users (id, username, email, password, phone_number, role)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id,
            username,
            email,
            hashed_password,
            phone_number,
            role,
        )
        return row["id"]

    async def create_password_reset_token(self, user_id, token_hash):
        query = """INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)"""
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        await self.conn.execute(
            query,
            user_id,
            token_hash,
            expires_at
        )

    async def get_valid_reset_token(self, token_hash: str):
        query = """
            SELECT *
            FROM password_reset_tokens
            WHERE token_hash = $1
            AND used = FALSE
            AND expires_at > now()"""
        return await self.conn.fetchrow(query, token_hash)

    async def mark_reset_token_used(self, token_hash: str):
        query = """
        UPDATE password_reset_tokens
        SET used = TRUE
        WHERE token_hash = $1
        """
        return self.conn.execute(query, token_hash)

    async def update_password(self, user_id, hashed_password):
        query = """
        UPDATE users
        SET password_hash = $1
        WHERE id = $2
        """
        await self.conn.execute(query, hashed_password, user_id)