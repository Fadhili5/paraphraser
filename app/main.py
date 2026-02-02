# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ex_router import api_router
from app.db.connection import init_db_pool
from app.db.schema import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    await create_tables()
    yield
    #await close_db_pool()

app = FastAPI(
    title="AI Paraphraser API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
