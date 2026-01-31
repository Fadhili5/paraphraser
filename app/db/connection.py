# db/connection.py
import asyncpg
from app.core.config import settings

db_pool = None

def _get_asyncpg_dsn():
    """Convert SQLAlchemy-style DSN to asyncpg-compatible DSN."""
    dsn = settings.DATABASE_URL
    return dsn.replace("postgresql+asyncpg://", "postgresql://")

async def init_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        dsn=_get_asyncpg_dsn(),
        ssl="require",
        min_size=1,
        max_size=10
    )

async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()

async def get_pool():
    return db_pool
