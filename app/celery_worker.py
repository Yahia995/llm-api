import time
from celery import Celery
import mlflow

from app.core.config import settings
from app.services.groq_service import generate_with_groq

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.worker_pool = "solo"
celery_app.conf.worker_concurrency = 1

mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)


@celery_app.task(name="generate_task", bind=True, max_retries=2)
def generate_task(self, prompt: str, model: str = None):
    start = time.time()
    mlflow.set_experiment("llm_inference")

    try:
        with mlflow.start_run():
            used_model = model or settings.GROQ_MODEL

            mlflow.log_param("model", used_model)
            mlflow.log_param("prompt_length", len(prompt))

            result = generate_with_groq(prompt, model=used_model)

            latency = time.time() - start
            mlflow.log_metric("latency_sec", round(latency, 3))
            mlflow.log_metric("prompt_tokens", result["prompt_tokens"])
            mlflow.log_metric("completion_tokens", result["completion_tokens"])
            mlflow.log_metric("total_tokens", result["total_tokens"])

            mlflow.log_text(result["response"], artifact_file="response.txt")

        result["latency_sec"] = round(latency, 3)
        return result

    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
