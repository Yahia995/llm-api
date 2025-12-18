from fastapi import APIRouter, HTTPException
from app.models.schemas import Prompt
from app.celery_worker import generate_task
from celery.result import AsyncResult
from app.core.config import settings

router = APIRouter()

@router.post("/generate")
def generate_text(data: Prompt):
    task = generate_task.delay(data.prompt)
    return {"task_id": task.id}

@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=generate_task.app)
    if result.ready():
        if result.successful():
            return {"status": "done", "result": result.result}
        else:
            return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": "pending"}