from app.db.connection import get_pool

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    role TEXT NOT NULL
);
"""

async def create_tables(app):
    pool = await get_pool(app)
    async with pool as conn:
        await conn.execute(CREATE_USERS_TABLE)

