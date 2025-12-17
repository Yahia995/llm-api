# LLM API with FastAPI (Async Version)

This project demonstrates a minimal Large Language Model (LLM) API built using *FastAPI* and connected to a locally running LLM served by *Ollama*.

The current version focuses on establishing a *working, clean, and extensible async API foundation*.
Future versions will progressively add background task processing, model tracking, and containerized deployment.

---

## 🚀 Features (Current Version)

* FastAPI REST API with async endpoints
* Async integration with a local LLM via Ollama using *httpx*
* Returns raw model output including metadata
* Simple and clean architecture ready for extension

---

## 🧠 Technology Stack (Current)

* Python 3.10+
* FastAPI
* Uvicorn
* httpx (async HTTP client)
* Ollama (local LLM runtime)

---

## 📦 Prerequisites

* Python 3.10 or higher
* Ollama installed and running
* A model pulled in Ollama (example: llama3)

To pull the model:

ollama pull llama3

To start Ollama:

ollama serve

---

## 🔧 Installation

Clone the repository and install dependencies:

pip install -r requirements.txt

Run the API:

uvicorn app.main:app --reload

The API will be available at:

http://localhost:8000

---

## 📖 API Documentation

FastAPI automatically provides interactive documentation:

* Swagger UI:
  👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔹 API Endpoint

### POST /generate

Generate text using the LLM.

#### Request Body

{
  "prompt": "What is 2 * 2?"
}

#### Response Example

{
  "model": "llama3",
  "created_at": "2025-12-17T11:51:13.4254271Z",
  "response": "2 * 2 equals 4!",
  "done": true,
  "eval_duration": 762040000,
  "prompt_eval_count": 17,
  "eval_count": 9
}

The API returns the **raw Ollama response**, including performance and evaluation metadata.
This design enables future integration with monitoring and experiment tracking tools.


---

## 🛠️ Project Status

✅ Async Ollama integration with httpx completed
✅ Async FastAPI endpoints in place
✅ Local LLM inference working
✅ API ready for extension

---

## 🔮 Planned Enhancements (Next Versions)

* Celery + Redis for background task processing
* Docker & Docker Compose for containerized deployment
* MLflow integration for model tracking and experiment management
* Hugging Face model registry and fallback inference support
* Authentication, rate limiting, and production hardening

---

## 📌 Notes

This repository follows an *incremental development approach*.
Each new feature is introduced in separate commits or branches to clearly demonstrate the system’s evolution.