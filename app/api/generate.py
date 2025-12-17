from fastapi import APIRouter, HTTPException
from app.models.schemas import Prompt
from app.services.ollama_service import generate_with_ollama

router = APIRouter()

@router.post("/generate")
async def generate_text(data: Prompt):
    try:
        return await generate_with_ollama(data.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))