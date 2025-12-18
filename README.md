# LLM API with FastAPI (Async + Celery Version)

This project demonstrates a minimal Large Language Model (LLM) API built using **FastAPI** and connected to a locally running LLM served by **Ollama**.

The current version introduces **background task processing using Celery and Redis**, enabling non-blocking LLM inference and improved scalability.

The project follows an **incremental development approach**, with each feature added in isolated commits.

---

## 🚀 Features (Current Version)

* FastAPI REST API
* Async endpoints using **httpx**
* Background LLM inference using **Celery**
* **Redis** as message broker and result backend
* Task-based request handling with result polling
* Centralized configuration using environment variables
* Returns raw model output including metadata

---

## 🧠 Technology Stack (Current)

* Python 3.10+
* FastAPI
* Uvicorn
* httpx
* Celery
* Redis
* pydantic-settings
* Ollama (local LLM runtime)

---

## 📦 Prerequisites

* Python 3.10 or higher
* Ollama installed and running
* Docker (recommended for Redis)
* A model pulled in Ollama (example: `llama3`)

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OLLAMA_URL=http://localhost:11434/api/generate
REDIS_URL=redis://localhost:6379/0
```

---

## ▶️ Running the Application

### 1️⃣ Start Redis (Docker recommended)

```bash
docker run -d -p 6379:6379 redis:7
```

---

### 2️⃣ Start Celery Worker (Windows ⚠️)

On **Windows**, Celery must be run using the `solo` pool due to multiprocessing limitations:

```bash
celery -A app.celery_worker worker --loglevel=info --pool=solo
```

> ⚠️ On Linux/macOS, production deployments typically use `prefork` or `gevent`.

---

### 3️⃣ Start FastAPI

```bash
uvicorn app.main:app --reload
```

API available at:

```
http://localhost:8000
```

---

## 📖 API Documentation

Swagger UI:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔹 API Endpoints

### POST `/generate`

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

### GET `/result/{task_id}`

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

## 🛠️ Project Status

✅ Async FastAPI API
✅ Celery + Redis background processing
✅ Windows-compatible Celery worker
✅ Centralized configuration
✅ Ready for Docker and MLOps extensions

---

## 🔮 Planned Enhancements

* Dockerfile + Docker Compose
* MLflow integration
* Hugging Face model registry
* Authentication & rate limiting
* Streaming responses

---

## 📌 Notes

This project is built **step by step** to clearly demonstrate:

* API scalability patterns
* Background job processing
* MLOps-ready architecture

Each major change is introduced in a **separate commit**.