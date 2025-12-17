from fastapi import FastAPI
from app.api.generate import router

app = FastAPI(title="LLM Async API")

app.include_router(router)