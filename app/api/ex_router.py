# app/api/ex_router.py
from fastapi import APIRouter

from app.users.route import router as users_router
from app.paraphrase.route import router as paraphrase_router

api_router = APIRouter()

api_router.include_router(users_router)
api_router.include_router(paraphrase_router)