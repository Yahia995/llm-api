import time
import logging
from celery import Celery

from app.core.config import settings
from app.services.groq_service import generate_with_groq

logger = logging.getLogger(__name__)

celery_app = Celery(
    "worker",
    broker=settings.redis_url_safe,
    backend=settings.redis_url_safe,
)

celery_app.conf.worker_pool = "solo"
celery_app.conf.worker_concurrency = 1

celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}
celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}


def log_to_mlflow(prompt: str, result: dict, latency: float):
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment("llm_inference")
        with mlflow.start_run():
            mlflow.log_param("model", result["model"])
            mlflow.log_param("prompt_length", len(prompt))
            mlflow.log_metric("latency_sec", round(latency, 3))
            mlflow.log_metric("prompt_tokens", result["prompt_tokens"])
            mlflow.log_metric("completion_tokens", result["completion_tokens"])
            mlflow.log_metric("total_tokens", result["total_tokens"])
            mlflow.log_text(result["response"], artifact_file="response.txt")
    except Exception as e:
        logger.warning(f"MLflow logging skipped: {e}")


@celery_app.task(name="generate_task", bind=True, max_retries=2)
def generate_task(self, prompt: str, model: str = None):
    start = time.time()
    try:
        result = generate_with_groq(prompt, model=model)
        latency = time.time() - start
        result["latency_sec"] = round(latency, 3)
        log_to_mlflow(prompt, result, latency)
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
