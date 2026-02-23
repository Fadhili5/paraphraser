# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ex_router import api_router
from app.db.connection import init_db_pool, close_db_pool
from app.db.schema import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool(app)
    await create_tables(app)
    yield
    # Shutdown
    await close_db_pool(app)

app = FastAPI(
    title="AI Paraphraser API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://paraphraser-six.vercel.app",
        "http://localhost:3000",
        "https://paraphraser-264w.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

app.include_router(api_router)
