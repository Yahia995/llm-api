from groq import Groq
from app.core.config import settings

def generate_with_groq(prompt: str, model: str = None) -> dict:
    client = Groq(api_key=settings.GROQ_API_KEY)
    model = model or settings.GROQ_MODEL

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    choice = completion.choices[0]
    return {
        "model": model,
        "response": choice.message.content,
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
        "finish_reason": choice.finish_reason,
    }
