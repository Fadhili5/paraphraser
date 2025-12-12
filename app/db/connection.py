# db/connection.py
import asyncpg
from app.core.config import settings

async def init_db_pool():
    return await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=10
    )

db_pool = None

async def get_pool():
    return db_pool
