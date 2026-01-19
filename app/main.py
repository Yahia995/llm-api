from fastapi import FastAPI
from app.api.generate import router

app = FastAPI(title="LLM API - learning Version")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "LLM API is running!"}
