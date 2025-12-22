import httpx
from app.core.config import settings

async def generate_with_ollama(prompt: str):
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(settings.OLLAMA_URL, json=payload)

    response.raise_for_status()
    return response.json()