from celery import Celery
from app.core.config import settings
from app.services.ollama_service import generate_with_ollama
import asyncio

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(bind=True)
def generate_task(self, prompt: str):
    # Since Celery tasks are sync by default, run the async function in an event loop
    return asyncio.run(generate_with_ollama(prompt))