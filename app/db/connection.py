# db/connection.py
import asyncpg
import asyncio
import re
from app.core.config import settings

db_pool = None

async def init_db_pool(app, retries=5, delay=3):
    db_url = settings.DATABASE_URL
    safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_url)
    print(f"Attempting to connect to {safe_url}")

    for attempt in range(1, retries + 1):
        try:
            app.state.db_pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                ssl="require",
                min_size=1,
                max_size=10,
                timeout=30,
                command_timeout=10
            )
            print(f"Database pool initialized successfully (attempt {attempt})")
            return
        except Exception as e:
            print(f"DB connection attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print("All connection attempts exhausted.")
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

