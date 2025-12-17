from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Simple LLM API")

OLLAMA_URL = "http://localhost:11434/api/generate"

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
def generate_text(data: Prompt):
    payload = {
        "model": "llama3",
        "prompt": data.prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))