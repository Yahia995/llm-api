import asyncio
from celery import Celery
import mlflow
import time

from app.core.config import settings
from app.services.ollama_service import generate_with_ollama

# Create Celery app
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,  # Where tasks are queued
    backend=settings.REDIS_URL  # Where results are stored
)

# Configure for Windows/WSL compatibility
celery_app.conf.worker_pool = "solo"
celery_app.conf.worker_concurrency = 1

# Configure MLflow
mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)

@celery_app.task(name="generate_task")
def generate_task(prompt: str):
    """
    Process LLM generation with MLflow tracking.
    Each task = one MLflow run.
    """
    start = time.time()
    
    mlflow.set_experiment("llm_inference")

    # Start MLflow run
    with mlflow.start_run():
        # Log parameters (inputs)
        mlflow.log_param("model", "llama3")
        mlflow.log_param("prompt", prompt)
        
        # Run the actual LLM inference
        result = asyncio.run(generate_with_ollama(prompt, settings.OLLAMA_URL))
        
        # Calculate latency
        latency = time.time() - start
        
        # Log metrics (measurements)
        mlflow.log_metric("latency_sec", latency)
        
        # Log artifact (full response as file)
        mlflow.log_text(
            result.get("response", ""),
            artifact_file="response.txt"
        )

    return result      
