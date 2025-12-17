import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"

async def generate_with_ollama(prompt: str):
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OLLAMA_URL, json=payload)

    response.raise_for_status()
    return response.json()