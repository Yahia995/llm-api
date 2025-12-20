# LLM API with FastAPI (Async + Celery Version)

This project demonstrates a minimal **Large Language Model (LLM) API** built using **FastAPI** and connected to a locally running LLM served by **Ollama**.

The current version introduces **background task processing** using **Celery** and **Redis**, enabling non-blocking LLM inference and improved scalability.

The project follows an **incremental development approach**, with each feature added in isolated commits.

---

## 🚀 Features (Current Version)

- ✅ **FastAPI REST API**
- ✅ **Async endpoints** using `httpx`
- ✅ **Background LLM inference** using Celery
- ✅ **Redis** as message broker and result backend
- ✅ **Task-based request handling** with result polling
- ✅ **Centralized configuration** using environment variables
- ✅ **Returns raw model output** including metadata
- ✅ **Dockerized services** with proper host-to-container networking
- ✅ **Windows/WSL2-compatible** Celery configuration (solo pool)

---

## 🧠 Technology Stack (Current)

- **Python 3.10+**
- **FastAPI**
- **Uvicorn**
- **httpx**
- **Celery**
- **Redis**
- **pydantic-settings**
- **Ollama** (local LLM runtime)
- **Docker & Docker Compose**

---

## 📦 Prerequisites

- Python 3.10 or higher
- Ollama installed and running
- Docker (recommended for Redis and containerized services)
- A model pulled in Ollama (example: `llama3`)

### Pull model:

```bash
ollama pull llama3
```

### Start Ollama:

```bash
ollama serve
```

---

## 🔧 Installation

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Create a `.env` file with:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
REDIS_URL=redis://redis:6379/0
```

**Note**: `host.docker.internal` is mapped via Docker Compose `extra_hosts` to enable container → host network access.

---

## ▶️ Running the Application

### 1️⃣ Start Docker Compose (Redis + API + Worker)

```bash
docker compose up --build
```

This will start:
- **Redis** (message broker)
- **FastAPI API** (web server)
- **Celery worker** (task processor)

---

### 2️⃣ On Windows/WSL2: Celery Worker Pool Configuration

Due to Windows limitations, Celery must run with the `solo` pool.

This is configured inside the worker service and/or when starting manually:

```bash
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

---

### 3️⃣ Access FastAPI

API is available at:

```
http://localhost:8000
```

---

## 📖 API Documentation

### Swagger UI:
👉 **http://localhost:8000/docs**

---

## 🔹 API Endpoints

### `POST /generate`

Submit a text generation request.

#### Request

```json
{
  "prompt": "Explain Celery in one sentence"
}
```

#### Response

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f"
}
```

---

### `GET /result/{task_id}`

Retrieve task status and result.

#### Response (Completed)

```json
{
  "status": "done",
  "result": {
    "model": "llama3",
    "response": "Celery is a distributed task queue used for background processing."
  }
}
```

#### Response (Pending)

```json
{
  "status": "pending"
}
```

---

## 🐳 Docker Configuration

### docker-compose.yml

```yaml
version: '3.9'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_URL=http://host.docker.internal:11434/api/generate
      - REDIS_URL=redis://redis:6379/0
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A app.celery_worker worker --loglevel=info --pool=solo
    environment:
      - OLLAMA_URL=http://host.docker.internal:11434/api/generate
      - REDIS_URL=redis://redis:6379/0
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_URL` | Ollama API endpoint | `http://host.docker.internal:11434/api/generate` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `MODEL_NAME` | Default LLM model | `llama3` |

---

## 🧪 Testing

### Manual Testing

**Submit a generation task:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is FastAPI?"}'
```

**Check task result:**
```bash
curl http://localhost:8000/result/{task_id}
```

---

## 🛠️ Development

### Run locally (without Docker)

**1. Start Redis:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**2. Start Celery worker:**
```bash
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

**3. Start FastAPI:**
```bash
uvicorn app.main:app --reload
```

---

## 🐛 Troubleshooting

### Common Issues

**Problem**: Celery worker fails on Windows
- **Solution**: Use `--pool=solo` flag

**Problem**: Cannot connect to Ollama
- **Solution**: Verify `host.docker.internal` mapping in `extra_hosts`

**Problem**: Redis connection refused
- **Solution**: Check Redis is running on port 6379

**Problem**: Task stuck in pending
- **Solution**: Check Celery worker logs: `docker compose logs worker`

---

## 🛠️ Project Status

| Feature | Status |
|---------|--------|
| Async FastAPI API | ✅ |
| Celery + Redis background processing | ✅ |
| Docker Compose multi-container orchestration | ✅ |
| Host-to-container network bridging | ✅ |
| Windows/WSL2-compatible configuration | ✅ |
| Centralized configuration with `.env` | ✅ |
| MLOps-ready architecture | ✅ |

---

## 🔮 Planned Enhancements

- [ ] **MLflow integration** for experiment tracking
- [ ] **Hugging Face model registry** and fallback inference
- [ ] **Authentication** and rate limiting
- [ ] **Streaming responses** support
- [ ] **Dockerized Ollama** with GPU support
- [ ] **Health check endpoints**
- [ ] **Request caching** with Redis
- [ ] **Batch processing** capabilities
- [ ] **Prometheus metrics** export
- [ ] **Grafana dashboards**

---

## 📌 Notes

This project is built **step-by-step** to clearly demonstrate:

- ✅ API scalability patterns
- ✅ Background job processing
- ✅ Distributed task management with Celery and Redis
- ✅ Host-container networking solutions on Windows and WSL2
- ✅ MLOps-ready architecture

Each major feature is introduced in a **separate commit** for clear incremental development and educational clarity.