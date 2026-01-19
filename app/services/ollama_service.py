import httpx

async def generate_with_ollama(prompt: str, ollama_url: str):
    """Call Ollama API to generate text"""
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(ollama_url, json=payload)

    response.raise_for_status()
    return response.json() 
