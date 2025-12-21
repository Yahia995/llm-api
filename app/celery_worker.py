import time
import asyncio
import mlflow
from celery import Celery

from app.core.config import settings
from app.services.ollama_service import generate_with_ollama

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Windows / WSL SAFE
celery_app.conf.worker_pool = "solo"
celery_app.conf.worker_concurrency = 1

mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
mlflow.set_experiment("llm-inference")


@celery_app.task(name="generate_task")
def generate_task(prompt: str):
    start = time.time()

    with mlflow.start_run():
        mlflow.log_param("model", "llama3")
        mlflow.log_param("prompt", prompt)

        # Run async code inside Celery
        result = asyncio.run(generate_with_ollama(prompt))

        latency = time.time() - start
        mlflow.log_metric("latency_sec", latency)

        mlflow.log_text(
            result.get("response", ""),
            artifact_file="response.txt"
        )

        return result