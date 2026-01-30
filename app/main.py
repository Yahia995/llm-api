from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import redis as redis_lib
import os

from app.api.generate import router
from app.core.config import settings

app = FastAPI(title="LLM API Platform", docs_url="/api/docs")

app.include_router(router)


@app.get("/health")
async def health():
    status = {"api": "ok", "redis": "unknown", "groq_key": "unknown"}

    try:
        r = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "unreachable"

    status["groq_key"] = "configured" if settings.GROQ_API_KEY else "missing"

    overall = "ok" if all(v in ("ok", "configured") for v in status.values()) else "degraded"
    return {"status": overall, "services": status}


STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
