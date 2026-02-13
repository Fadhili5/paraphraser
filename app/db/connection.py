# db/connection.py
import asyncpg
from app.core.config import settings

db_pool = None


async def init_db_pool(app):

    db_url = settings.DATABASE_URL

    import re
    safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_url)
    print(f"Attempting to connect to {safe_url}")

    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            ssl='prefer',  # Changed from "require" string
            min_size=1,
            max_size=10,
            timeout=30,
            command_timeout=10
        )
        print("DATABASE_URL seen by app:", settings.DATABASE_URL)
        print("Database pool initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database pool: {e}")
        raise


async def get_pool(app):
    pool = getattr(app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("Database pool not initialized")
    return pool


async def close_db_pool(app):
    pool = getattr(app.state, "db_pool", None)
    if pool:
        await pool.close()
