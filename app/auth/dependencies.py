from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import asyncpg

from app.auth.jwt import decode_access_token
from app.users.dao import UserDAO
from app.db.connection import get_pool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_pool: asyncpg.pool.Pool = Depends(get_pool),
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    async with db_pool.acquire() as conn:
        dao = UserDAO(conn)
        user = await dao.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
