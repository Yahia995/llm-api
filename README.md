<div align="center">

# LLM API Platform

**Model-agnostic inference service with async processing and experiment tracking**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square)](https://groq.com)
[![Celery](https://img.shields.io/badge/Celery-a9cc54?style=flat-square&logo=celery)](https://docs.celeryproject.org/)
[![Redis](https://img.shields.io/badge/Redis-DD0031?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-0db7ed?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

🔗 **[Live Demo](https://llm-api-0z1b.onrender.com)**

</div>

---

## What problem this solves

Switching between LLM providers or models usually means rewriting integration code. This platform puts a consistent async API in front of any Groq-hosted model — you swap the model name, everything else stays the same. Every inference request is automatically tracked in MLflow (latency, token usage, model used), so you can compare models on real workloads rather than benchmarks.

The practical use case: run the same prompt across `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, and `llama-4-scout` and immediately see the latency/quality tradeoff in the dashboard.

---

## Architecture

```
Client
  │
  ▼
FastAPI  ──── submits task ────▶  Redis Queue
  │                                    │
  │  ◀──── polls /status/{id} ────  Celery Worker
  │                                    │
  │                              Groq Cloud API
  │                                    │
  ▼                              MLflow → Neon Postgres
Dashboard ◀──── /metrics ───────────────┘
```

The API returns a `task_id` immediately — inference happens in the background. The dashboard polls until the result is ready, then renders it with latency and token stats.

---

## Stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI + uvicorn | Async endpoints, automatic OpenAPI docs |
| Task queue | Celery + Redis (Upstash) | Non-blocking inference, retries on failure |
| LLM provider | Groq Cloud | Fastest inference API available, generous free tier |
| Experiment tracking | MLflow → Neon Postgres | Persistent metrics without a dedicated server |
| Deployment | Render (Docker) | Single-container, free tier, zero config |
| Frontend | Vanilla JS | No build step, loads instantly |

---

## Local setup

**Requires:** Docker + Docker Compose

```bash
git clone https://github.com/Yahia995/llm-api
cd llm-api

cp .env.example .env
# Add GROQ_API_KEY and DATABASE_URL at minimum

docker compose up --build
```

Open **http://localhost:8000**

---

## API

```bash
# Submit a prompt (returns immediately)
curl -X POST https://your-app.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compare quicksort and mergesort", "model": "llama-3.1-8b-instant"}'

# → {"task_id": "abc123", "status": "queued", "check_url": "/status/abc123"}

# Poll for result
curl https://your-app.onrender.com/status/abc123

# Aggregated metrics across all runs
curl https://your-app.onrender.com/metrics

# Health check
curl https://your-app.onrender.com/health
```

**Available models**

| ID | Best for |
|---|---|
| `llama-3.1-8b-instant` | Speed, simple tasks |
| `llama-3.3-70b-versatile` | Quality, reasoning |
| `openai/gpt-oss-20b` | Balanced |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Latest Meta model |

---

## Environment variables

| Variable | Description | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | Groq inference key | [console.groq.com](https://console.groq.com) |
| `REDIS_URL` | `rediss://` connection string | [upstash.com](https://upstash.com) |
| `DATABASE_URL` | Postgres connection string | [neon.tech](https://neon.tech) |
| `GROQ_MODEL` | Default model | See table above |

---

## Deployment

Single Render web service running API + Celery worker via `supervisord`.

```bash
# 1. Push to GitHub
# 2. Render → New → Blueprint → select repo
# 3. Set GROQ_API_KEY, REDIS_URL, DATABASE_URL as secrets
# 4. Deploy
```

---

## What's tracked per run

| Metric | Description |
|---|---|
| `latency_sec` | Wall-clock time from task start to response |
| `prompt_tokens` | Input token count |
| `completion_tokens` | Output token count |
| `total_tokens` | Sum |
| `model` | Which model handled the request |

---

## Project structure

```
llm-api/
├── app/
│   ├── main.py                 # FastAPI app, health, static serving
│   ├── celery_worker.py        # Task execution + MLflow logging
│   ├── api/generate.py         # /generate /status /metrics endpoints
│   ├── services/groq_service.py
│   ├── core/config.py
│   ├── models/schemas.py
│   └── static/index.html       # Dashboard UI
├── supervisord.conf             # Runs API + worker in one container
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── .env.example
```

---

## Roadmap

- [ ] Side-by-side model comparison (same prompt → multiple models → compare)
- [ ] Streaming responses via WebSocket
- [ ] Request caching
- [ ] Rate limiting + API key auth
- [ ] Prometheus metrics export

---

<div align="center">
Built by <a href="https://github.com/Yahia995">Yahia Achouri</a>
</div>
