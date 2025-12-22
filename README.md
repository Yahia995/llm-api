# LLM API with FastAPI (Async + Celery + MLflow Version)

This project demonstrates a minimal **Large Language Model (LLM) API** built using **FastAPI** and connected to a locally running LLM served by **Ollama**.

The current version introduces **background task processing** using **Celery** and **Redis**, enabling non-blocking LLM inference and improved scalability, along with **MLflow integration** for experiment tracking and monitoring inference jobs.

The project follows an **incremental development approach**, with each feature added in isolated commits.

---

## 🚀 Features (Current Version)

* ✅ **FastAPI REST API**
* ✅ **Async endpoints** using `httpx`
* ✅ **Background LLM inference** using Celery
* ✅ **Redis** as message broker and result backend
* ✅ **Task-based request handling** with result polling
* ✅ **Centralized configuration** using environment variables
* ✅ **Returns raw model output** including metadata
* ✅ **Dockerized services** with proper host-to-container networking
* ✅ **Windows/WSL2-compatible** Celery configuration (solo pool)
* ✅ **MLflow integration** for tracking inference requests, parameters, latency, and artifacts

---

## 🧠 Technology Stack (Current)

* **Python 3.10+**
* **FastAPI**
* **Uvicorn**
* **httpx**
* **Celery**
* **Redis**
* **pydantic-settings**
* **Ollama** (local LLM runtime)
* **MLflow** (experiment tracking & metrics)
* **Docker & Docker Compose**

---

## 🔧 Installation & Setup

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Create `.env` file:

```env
OLLAMA_URL=http://host.docker.internal:11434/api/generate
REDIS_URL=redis://redis:6379/0
MLFLOW_TRACKING_URI=http://mlflow:5000
HUGGING_FACE_TOKEN=your_huggingface_token_here
```

**Note**: `host.docker.internal` is mapped via Docker Compose `extra_hosts` to enable container → host network access.

---

## ▶️ Running the Application

### 1️⃣ Start Docker Compose (Redis + API + Worker + MLflow)

```bash
docker compose up --build
```

This starts:

* **Redis** (message broker)
* **FastAPI API** (web server)
* **Celery worker** (task processor)
* **MLflow server** (tracking UI & API)

---

### 2️⃣ On Windows/WSL2: Celery Worker Pool Configuration

Due to Windows limitations, Celery runs with the `solo` pool.

Configured in worker service startup:

```bash
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

---

### 3️⃣ Access FastAPI

```
http://localhost:8000
```

---

### 4️⃣ Access MLflow UI

```
http://localhost:5000
```

---

## 📖 API Documentation

### Swagger UI:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

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
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mlflow:
    build: ./mlflow
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow/mlruns:/mlflow/mlruns

  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis
      - mlflow

  worker:
    build: .
    command: celery -A app.celery_worker worker --loglevel=info --pool=solo
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis
      - mlflow
```

---

## ⚙️ Configuration

### Environment Variables

| Variable              | Description                | Default                                          |
| --------------------- | -------------------------- | ------------------------------------------------ |
| `OLLAMA_URL`          | Ollama API endpoint        | `http://host.docker.internal:11434/api/generate` |
| `REDIS_URL`           | Redis connection URL       | `redis://redis:6379/0`                           |
| `MLFLOW_TRACKING_URI` | MLflow server tracking URI | `http://mlflow:5000`                             |
| `HUGGING_FACE_TOKEN`  | Token for Hugging Face API | (optional)                                       |

---

## 🛠️ Development

### Run locally (without Docker)

1. Start Redis:

```bash
docker run -d -p 6379:6379 redis:7
```

2. Start MLflow server:

```bash
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow/mlflow.db --default-artifact-root ./mlflow/mlruns --serve-artifacts
```

3. Start Celery worker:

```bash
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

4. Start FastAPI:

```bash
uvicorn app.main:app --reload
```

---

## 🐛 Troubleshooting

* **Celery worker fails on Windows**
  Use `--pool=solo` flag for Celery.

* **Cannot connect to Ollama**
  Verify `host.docker.internal` mapping in `extra_hosts`.

* **Redis connection refused**
  Ensure Redis is running on port 6379.

* **Task stuck in pending**
  Check Celery worker logs: `docker compose logs worker`.

* **MLflow UI not reachable**
  Confirm MLflow container is running and port 5000 is exposed.

---

## 🛠️ Project Status

| Feature                                      | Status |
| -------------------------------------------- | ------ |
| Async FastAPI API                            | ✅      |
| Celery + Redis background processing         | ✅      |
| Docker Compose multi-container orchestration | ✅      |
| Host-to-container network bridging           | ✅      |
| Windows/WSL2-compatible configuration        | ✅      |
| Centralized configuration with `.env`        | ✅      |
| MLOps-ready architecture with MLflow         | ✅      |

---

## 🔮 Planned Enhancements

* [ ] **Hugging Face model registry** and fallback inference
* [ ] **Authentication** and rate limiting
* [ ] **Streaming responses** support
* [ ] **Dockerized Ollama** with GPU support
* [ ] **Health check endpoints**
* [ ] **Request caching** with Redis
* [ ] **Batch processing** capabilities
* [ ] **Prometheus metrics** export
* [ ] **Grafana dashboards**

---

## 📌 Notes

This project is built **step-by-step** to clearly demonstrate:

* ✅ API scalability patterns
* ✅ Background job processing
* ✅ Distributed task management with Celery and Redis
* ✅ Host-container networking solutions on Windows and WSL2
* ✅ MLOps-ready architecture with MLflow tracking

Each major feature is introduced in a **separate commit** for clear incremental development and educational clarity.