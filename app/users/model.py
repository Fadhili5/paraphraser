from datetime import datetime
from uuid import uuid4

class UserModel:
    """
    Raw SQL user model.
    Handles: creation, fetch, login lookup.
    DB dependency is passed in, no ORM.
    """

    @staticmethod
    async def create_user(conn, email: str, hashed_password: str):
        user_id = str(uuid4())
        now = datetime.utcnow()

        query = """
            INSERT INTO users (id, email, password, created_at)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, created_at;
        """

        row = await conn.fetchrow(query, user_id, email, hashed_password, now)
        return dict(row)

    @staticmethod
    async def get_user_by_email(conn, email: str):
        query = """
            SELECT id, email, password, created_at
            FROM users
            WHERE email = $1
            LIMIT 1;
        """
        row = await conn.fetchrow(query, email)
        return dict(row) if row else None

    @staticmethod
    async def get_user_by_id(conn, user_id: str):
        query = """
            SELECT id, email, created_at
            FROM users
            WHERE id = $1;
        """
        row = await conn.fetchrow(query, user_id)
        return dict(row) if row else None
