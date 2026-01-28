from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
import mlflow

from app.models.schemas import Prompt
from app.celery_worker import generate_task
from app.core.config import settings

router = APIRouter()

@router.post("/generate")
async def generate(data: Prompt):
    task = generate_task.delay(data.prompt, data.model)
    return {
        "task_id": task.id,
        "status": "queued",
        "check_url": f"/status/{task.id}",
    }

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    task = AsyncResult(task_id)

    if task.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING", "result": None}
    elif task.state == "PROGRESS":
        return {"task_id": task_id, "status": "PROGRESS", "result": task.info}
    elif task.state == "SUCCESS":
        return {"task_id": task_id, "status": "SUCCESS", "result": task.result}
    else:
        return {"task_id": task_id, "status": task.state, "error": str(task.info)}

async def get_metrics():
    try:
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()

        experiment = client.get_experiment_by_name("llm_inference")
        if experiment is None:
            return {"runs": [], "summary": {}}

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=50,
        )

        run_data = []
        for run in runs:
            m = run.data.metrics
            p = run.data.params
            run_data.append({
                "run_id": run.info.run_id,
                "start_time": run.info.start_time,
                "model": p.get("model", "unknown"),
                "latency_sec": m.get("latency_sec"),
                "prompt_tokens": m.get("prompt_tokens"),
                "completion_tokens": m.get("completion_tokens"),
                "total_tokens": m.get("total_tokens"),
                "prompt_length": p.get("prompt_length"),
            })

        latencies = [r["latency_sec"] for r in run_data if r["latency_sec"] is not None]
        tokens = [r["total_tokens"] for r in run_data if r["total_tokens"] is not None]

        summary = {
            "total_runs": len(run_data),
            "avg_latency_sec": round(sum(latencies) / len(latencies), 3) if latencies else 0,
            "min_latency_sec": round(min(latencies), 3) if latencies else 0,
            "max_latency_sec": round(max(latencies), 3) if latencies else 0,
            "total_tokens_used": int(sum(tokens)),
            "avg_tokens_per_run": round(sum(tokens) / len(tokens), 1) if tokens else 0,
        }

        return {"runs": run_data, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MLflow error: {str(e)}")
