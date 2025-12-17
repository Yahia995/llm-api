# LLM API with FastAPI (Initial Version)

This project demonstrates a minimal Large Language Model (LLM) API built using **FastAPI** and connected to a locally running LLM served by **Ollama**.

The current version focuses on establishing a **working, clean, and extensible API foundation**.  
Future versions will progressively add background task processing, model tracking, and containerized deployment.

---

## 🚀 Features (Current Version)

- FastAPI REST API
- Text generation endpoint
- Integration with a local LLM via Ollama
- Returns raw model output including metadata
- Simple and clean architecture ready for extension

---

## 🧠 Technology Stack (Initial)

- Python 3.10+
- FastAPI
- Uvicorn
- Requests
- Ollama (local LLM runtime)

---

## 📦 Prerequisites

- Python 3.10 or higher
- Ollama installed and running
- A model pulled in Ollama (example: `llama3`)

To pull the model:
```bash
ollama pull llama3
````

To start Ollama:

```bash
ollama serve
```

---

## 🔧 Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

---

## 📖 API Documentation

FastAPI automatically provides interactive documentation:

* Swagger UI:
  👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔹 API Endpoint

### POST `/generate`

Generate text using the LLM.

#### Request Body

```json
{
  "prompt": "What is 2 * 2?"
}
```

#### Response Example

```json
{
  "model": "llama3",
  "created_at": "2025-12-17T11:51:13.4254271Z",
  "response": "2 * 2 equals 4!",
  "done": true,
  "eval_duration": 762040000,
  "prompt_eval_count": 17,
  "eval_count": 9
}
```

> The API intentionally returns the **raw Ollama response**, including performance and evaluation metadata.
> This design enables future integration with monitoring and experiment tracking tools.

---

## 🛠️ Project Status

✅ Initial version completed
✅ Local LLM inference working
✅ API ready for extension

---

## 🔮 Planned Enhancements (Next Versions)

* Asynchronous request handling
* Celery + Redis for background tasks
* Docker & Docker Compose setup
* MLflow integration for model tracking
* Hugging Face model registry support
* Authentication and rate limiting

---

## 📌 Notes

This repository follows an **incremental development approach**.
Each new feature will be introduced in separate commits to clearly demonstrate the system’s evolution.