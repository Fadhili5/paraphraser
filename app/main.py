# main.py
from fastapi import FastAPI
from app.users.route import router as users_router
from app.paraphrase.route import router as paraphrase_router

app = FastAPI(
    title="AI Paraphraser",
    version="1.0.0"
)

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(paraphrase_router, prefix="/paraphrase", tags=["Paraphraser"])

@app.get("/")
def root():
    return {"message": "Paraphraser API is running"}
