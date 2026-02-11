from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from pydantic import BaseModel
from typing import Optional

from app.celery_worker import celery_app, generate_task, arena_task
from app.core.config import settings
from app.services.groq_service import (
    classify_prompt,
    AVAILABLE_MODELS,
    ROUTING_TABLE,
)

router = APIRouter()


class Prompt(BaseModel):
    prompt: str
    model:  Optional[str] = None


class RouteRequest(BaseModel):
    prompt: str


class ArenaRequest(BaseModel):
    prompt: str
    models: Optional[list[str]] = None 


@router.post("/generate")
async def generate(data: Prompt):
    task = generate_task.delay(data.prompt, data.model)
    return {"task_id": task.id, "status": "queued", "check_url": f"/status/{task.id}"}


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    if task.state   == "PENDING":  return {"task_id": task_id, "status": "PENDING",  "result": None}
    elif task.state == "PROGRESS": return {"task_id": task_id, "status": "PROGRESS", "result": task.info}
    elif task.state == "SUCCESS":  return {"task_id": task_id, "status": "SUCCESS",  "result": task.result}
    else:                          return {"task_id": task_id, "status": task.state,  "error":  str(task.info)}


@router.post("/route")
async def route(data: RouteRequest):
    classification = classify_prompt(data.prompt)
    model          = classification["recommended_model"]
    task           = generate_task.delay(
        data.prompt,
        model,
        task_type=classification["task_type"],
        routed=True,
    )
    return {
        "task_id":           task.id,
        "status":            "queued",
        "check_url":         f"/status/{task.id}",
        "classification":    classification,
        "selected_model":    model,
        "model_label":       AVAILABLE_MODELS.get(model, {}).get("label", model),
    }


@router.post("/arena")
async def arena(data: ArenaRequest):
    models = data.models or list(AVAILABLE_MODELS.keys())
    tasks  = {}
    for model in models:
        t = arena_task.delay(data.prompt, model)
        tasks[model] = {
            "task_id":    t.id,
            "model":      model,
            "model_label": AVAILABLE_MODELS.get(model, {}).get("label", model),
            "check_url":  f"/status/{t.id}",
        }
    return {"prompt": data.prompt, "tasks": tasks}


@router.get("/models")
async def get_models():
    return {"models": AVAILABLE_MODELS, "routing_table": ROUTING_TABLE}


@router.get("/metrics")
async def get_metrics():
    try:
        import mlflow
        tracking_uri = settings.DATABASE_URL if settings.DATABASE_URL else settings.MLFLOW_TRACKING_URI
        mlflow.set_tracking_uri(tracking_uri)
        client = mlflow.tracking.MlflowClient()

        experiment = client.get_experiment_by_name("llm_inference")
        if experiment is None:
            return {"runs": [], "summary": {}, "leaderboard": []}

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=200,
        )

        run_data = []
        for run in runs:
            m = run.data.metrics
            p = run.data.params
            run_data.append({
                "run_id":           run.info.run_id,
                "start_time":       run.info.start_time,
                "model":            p.get("model", "unknown"),
                "task_type":        p.get("task_type", "unknown"),
                "routed":           p.get("routed", "False") == "True",
                "latency_sec":      m.get("latency_sec"),
                "prompt_tokens":    m.get("prompt_tokens"),
                "completion_tokens":m.get("completion_tokens"),
                "total_tokens":     m.get("total_tokens"),
            })

        latencies = [r["latency_sec"]  for r in run_data if r["latency_sec"]  is not None]
        tokens    = [r["total_tokens"] for r in run_data if r["total_tokens"] is not None]

        summary = {
            "total_runs":         len(run_data),
            "avg_latency_sec":    round(sum(latencies) / len(latencies), 3) if latencies else 0,
            "min_latency_sec":    round(min(latencies), 3)                  if latencies else 0,
            "max_latency_sec":    round(max(latencies), 3)                  if latencies else 0,
            "total_tokens_used":  int(sum(tokens)),
            "avg_tokens_per_run": round(sum(tokens) / len(tokens), 1)       if tokens    else 0,
        }

        from collections import defaultdict
        model_stats = defaultdict(lambda: {"runs": 0, "latencies": [], "tokens": [], "wins": 0})

        for r in run_data:
            m = r["model"]
            model_stats[m]["runs"] += 1
            if r["latency_sec"]  is not None: model_stats[m]["latencies"].append(r["latency_sec"])
            if r["total_tokens"] is not None: model_stats[m]["tokens"].append(r["total_tokens"])

        avg_lat = summary["avg_latency_sec"] or 999
        for r in run_data:
            if r["latency_sec"] is not None and r["latency_sec"] < avg_lat:
                model_stats[r["model"]]["wins"] += 1

        leaderboard = []
        for model, s in model_stats.items():
            lats = s["latencies"]
            toks = s["tokens"]
            leaderboard.append({
                "model":            model,
                "model_label":      AVAILABLE_MODELS.get(model, {}).get("label", model),
                "runs":             s["runs"],
                "avg_latency_sec":  round(sum(lats) / len(lats), 3) if lats else None,
                "avg_tokens":       round(sum(toks) / len(toks), 1) if toks else None,
                "wins":             s["wins"],
                "win_rate":         round(s["wins"] / s["runs"] * 100) if s["runs"] else 0,
            })

        leaderboard.sort(key=lambda x: x["avg_latency_sec"] or 999)

        return {"runs": run_data[:50], "summary": summary, "leaderboard": leaderboard}

    except Exception as e:
        return {"runs": [], "summary": {}, "leaderboard": [], "warning": str(e)}
