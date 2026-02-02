# db/connection.py
import asyncpg
from app.core.config import settings

db_pool = None


async def init_db_pool():
    global db_pool

    try:
        db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            ssl='prefer',  # Changed from "require" string
            min_size=1,
            max_size=10,
            timeout=30,
            command_timeout=10
        )
        print("Database pool initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database pool: {e}")
        raise


async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None


async def get_pool():
    if db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return db_pool