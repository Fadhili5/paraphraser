import asyncpg
from typing import Optional
from app.users.model import UserDB


class UserDAO:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_by_email(self, email: str) -> Optional[UserDB]:
        row = await self.conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        return UserDB(**dict(row)) if row else None

    async def get_by_email_and_username(self, email: str, username: str) -> Optional[UserDB]:
        row = await self.conn.fetchrow(
            """
            SELECT * FROM users
            WHERE email = $1 OR username = $2
            """,
            email, username
        )
        return UserDB(**dict(row)) if row else None

    async def create_user(self, user_id: str, username: str, email: str, hashed_password: str, phone: str, role: str = "user") -> str:
        row = await self.conn.fetchrow(
            """
            INSERT INTO users (id, username, email, password, phone, role)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id, username, email, hashed_password, phone, role
        )
        return row["id"]
