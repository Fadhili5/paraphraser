from fastapi import APIRouter, Request
from app.core.rate_limit import rate_limit

router = APIRouter()

@router.get("/preview")
@rate_limit(limit=10, window=60)
async def preview(request: Request):
    return {"message": "Still under rate limit."}
