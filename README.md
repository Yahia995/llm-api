<div align="center">

# LLM API Platform

**Async AI inference service with real-time experiment tracking**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=data:image/svg+xml;base64,PHN2Zy8+)](https://groq.com)
[![Celery](https://img.shields.io/badge/Celery-a9cc54?style=flat-square&logo=celery)](https://docs.celeryproject.org/)
[![Redis](https://img.shields.io/badge/Redis-DD0031?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-0db7ed?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

🔗 **[Live Demo](https://your-app.koyeb.app)** &nbsp;·&nbsp; 📊 **[MLflow Dashboard](https://mlflow.your-app.koyeb.app)**

</div>

---

## What this is

A production-style API platform that wraps Groq's LLM inference behind an async task queue, with every request automatically tracked in MLflow. Built to demonstrate real MLOps patterns: async processing, experiment tracking, metrics aggregation, and containerized deployment.

The frontend is a custom dashboard (no Swagger UI) where you can send prompts, watch responses arrive in real-time, and monitor latency/token metrics across all runs — side by side.

---

## Architecture

```
Client → FastAPI → Redis Queue → Celery Worker → Groq API
                ↘                      ↓
              /status/{id}          MLflow (Neon Postgres)
                ↗                      ↓
           Dashboard ←──── /metrics endpoint
```

**Stack:**

| Layer | Technology |
|---|---|
| API | FastAPI + uvicorn |
| Task queue | Celery + Redis |
| LLM provider | Groq Cloud (llama3, mixtral, gemma2) |
| Experiment tracking | MLflow |
| Tracking DB | Neon Postgres (serverless) |
| Deployment | Koyeb |
| Frontend | Vanilla JS dashboard |

---

## Local setup

**Requirements:** Docker + Docker Compose

```bash
git clone https://github.com/<you>/llm-api
cd llm-api

cp .env.example .env
# Edit .env — add your GROQ_API_KEY and DATABASE_URL at minimum

docker compose up --build
```

Open **http://localhost:8000** for the dashboard, **http://localhost:5000** for MLflow.

**Get a free Groq key:** https://console.groq.com  
**Get a free Neon Postgres DB:** https://neon.tech

---

## API

```bash
# Submit a prompt
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain Redis in one sentence", "model": "llama3-8b-8192"}'
# → {"task_id": "abc123", "status": "queued", "check_url": "/status/abc123"}

# Poll for result
curl http://localhost:8000/status/abc123

# Aggregated metrics (last 50 runs)
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/health
```

**Supported models:** `llama3-8b-8192` · `llama3-70b-8192` · `mixtral-8x7b-32768` · `gemma2-9b-it`

---

## Quick demo script

```bash
# Test local
python demo.py

# Test live deployment
python demo.py https://your-app.koyeb.app "Explain async queues in two sentences"
```

---

## Project structure

```
llm-api/
├── app/
│   ├── main.py              # FastAPI app, health check, static serving
│   ├── celery_worker.py     # Celery task + MLflow logging
│   ├── api/generate.py      # /generate, /status, /metrics endpoints
│   ├── services/groq_service.py   # Groq SDK wrapper
│   ├── core/config.py       # Pydantic settings
│   ├── models/schemas.py    # Request schemas
│   └── static/index.html    # Dashboard UI
├── mlflow/
│   └── Dockerfile           # MLflow server (Postgres backend)
├── Dockerfile               # API + Worker image
├── docker-compose.yml
├── koyeb.yaml               # Koyeb deployment config
├── demo.py                  # CLI smoke test
└── .env.example
```

---

## Deployment (Render)

1. Push this repo to GitHub
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint** → select your repo
3. Render detects `render.yaml` and creates all 3 services automatically
4. Set these secrets in the Render dashboard:

| Secret | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `REDIS_URL` | [upstash.com](https://upstash.com) — free Redis |
| `DATABASE_URL` | [neon.tech](https://neon.tech) — free Postgres |

Three services deploy: **llm-api** (web), **llm-worker** (background worker), **llm-mlflow** (web). The API and worker automatically get the MLflow URL injected via `fromService`.

---

## What's tracked per inference run

| Metric | Description |
|---|---|
| `latency_sec` | Wall-clock time from task start to response |
| `prompt_tokens` | Input token count |
| `completion_tokens` | Output token count |
| `total_tokens` | Sum of both |
| `model` | Model used (param) |
| `prompt_length` | Character count of input (param) |

Full response text is stored as an MLflow artifact (`response.txt`) per run.

---

## Roadmap

- [ ] Streaming responses via WebSocket
- [ ] Request caching layer (Redis)
- [ ] Rate limiting + API key auth
- [ ] Prometheus metrics export
- [ ] Batch inference endpoint

---

<div align="center">
Built by <a href="https://github.com/Yahia995">Yahia Achouri</a>
</div>
