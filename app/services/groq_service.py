from groq import Groq
from app.core.config import settings

AVAILABLE_MODELS = {
    "llama-3.1-8b-instant": {
        "label": "Llama 3.1 8B",
        "speed": "fastest",
        "best_for": ["factual", "summarization", "creative"],
        "cost_tier": 1,
    },
    "llama-3.3-70b-versatile": {
        "label": "Llama 3.3 70B",
        "speed": "medium",
        "best_for": ["reasoning", "code", "analysis"],
        "cost_tier": 3,
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "label": "Llama 4 Scout",
        "speed": "fast",
        "best_for": ["reasoning", "code", "factual"],
        "cost_tier": 2,
    },
    "compound-beta": {
        "label": "Compound Beta",
        "speed": "medium",
        "best_for": ["code", "analysis", "reasoning"],
        "cost_tier": 2,
    },
}

ROUTING_TABLE = {
    "code":          "llama-3.3-70b-versatile",
    "reasoning":     "llama-3.3-70b-versatile",
    "analysis":      "meta-llama/llama-4-scout-17b-16e-instruct",
    "factual":       "llama-3.1-8b-instant",
    "summarization": "llama-3.1-8b-instant",
    "creative":      "llama-3.1-8b-instant",
}


def generate_with_groq(prompt: str, model: str = None) -> dict:
    client = Groq(api_key=settings.GROQ_API_KEY)
    model  = model or settings.GROQ_MODEL

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    choice = completion.choices[0]
    return {
        "model":             model,
        "response":          choice.message.content,
        "prompt_tokens":     completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens":      completion.usage.total_tokens,
        "finish_reason":     choice.finish_reason,
    }


def classify_prompt(prompt: str) -> dict:
    client = Groq(api_key=settings.GROQ_API_KEY)

    system = """You are a prompt classifier. Given a user prompt, respond with ONLY a JSON object:
{
  "task_type": "<one of: code, reasoning, analysis, factual, summarization, creative>",
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explaining the classification>",
  "recommended_model": "<model id>"
}

Task type definitions:
- code: writing, debugging, explaining code
- reasoning: logic puzzles, math, multi-step thinking
- analysis: comparing options, evaluating tradeoffs, structured analysis  
- factual: questions with clear factual answers, definitions, lookups
- summarization: condensing text, extracting key points
- creative: stories, poems, brainstorming, open-ended writing

Routing rules:
- code → llama-3.3-70b-versatile
- reasoning → llama-3.3-70b-versatile
- analysis → meta-llama/llama-4-scout-17b-16e-instruct
- factual → llama-3.1-8b-instant
- summarization → llama-3.1-8b-instant
- creative → llama-3.1-8b-instant

Return ONLY the JSON, no markdown, no explanation."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        import json
        raw = completion.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        assert "task_type" in result and "recommended_model" in result
        return result
    except Exception:
        return {
            "task_type":         "factual",
            "confidence":        0.5,
            "reasoning":         "Could not classify — using default model.",
            "recommended_model": settings.GROQ_MODEL,
        }
