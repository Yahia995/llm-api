from fastapi import APIRouter
from app.models.schemas import Prompt
from app.celery_worker import generate_task
from celery.result import AsyncResult

router = APIRouter()

@router.post("/generate")
async def generate(data: Prompt):
    """Dispatch LLM generation task to Celery"""
    task = generate_task.delay(data.prompt)
    return {
        "task_id": task.id,
        "status": "Task submitted",
        "check_url": f"/status/{task.id}"
    }

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Check task status and get results"""
    task = AsyncResult(task_id)
    
    if task.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING", "result": None}
    elif task.state == "PROGRESS":
        return {"task_id": task_id, "status": "PROGRESS", "result": task.info}
    elif task.state == "SUCCESS":
        return {"task_id": task_id, "status": "SUCCESS", "result": task.result}
    else:
        return {"task_id": task_id, "status": task.state, "error": str(task.info)}
