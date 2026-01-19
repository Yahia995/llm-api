# LLM API with FastAPI (Async + Celery + MLflow Version)

This project demonstrates a minimal **Large Language Model (LLM) API** built using **FastAPI** and connected to a locally running LLM served by **Ollama**.

The current version introduces **background task processing** using **Celery** and **Redis**, enabling non-blocking LLM inference and improved scalability, along with **MLflow integration** for experiment tracking and monitoring inference jobs.

**NEW**: Ollama is now fully containerized with automatic model pulling and persistent storage!

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
* ✅ **Fully containerized stack** - no host dependencies
* ✅ **Windows/WSL2-compatible** Celery configuration (solo pool)
* ✅ **MLflow integration** for tracking inference requests, parameters, latency, and artifacts
* ✅ **Containerized Ollama** with automatic model management
* ✅ **Persistent model storage** via Docker volumes

---

## 🧠 Technology Stack (Current)

* **Python 3.10+**
* **FastAPI**
* **Uvicorn**
* **httpx**
* **Celery**
* **Redis**
* **pydantic-settings**
* **Ollama** (containerized LLM runtime with auto model download)
* **MLflow** (experiment tracking & metrics)
* **Docker & Docker Compose**

---

## 🔧 Installation & Setup

### Prerequisites

- **Docker** and **Docker Compose** installed
- That's it! No need to install Ollama separately

### Install Python dependencies (for local development only):

```bash
pip install -r requirements.txt
```

### Create `.env` file:

```env
OLLAMA_URL=http://ollama:11434/api/generate
REDIS_URL=redis://redis:6379/0
MLFLOW_TRACKING_URI=http://mlflow:5000
```

**Note**: All services communicate via Docker network using service names (e.g., `ollama`, `redis`, `mlflow`)

---

## ▶️ Running the Application

### Start Everything with Docker Compose

```bash
docker compose up --build
```

This single command starts:

* **Redis** (message broker)
* **Ollama** (LLM runtime - automatically pulls llama3 model on first run)
* **MLflow** (experiment tracking & metrics UI)
* **FastAPI API** (web server)
* **Celery worker** (background task processor)

**First-time setup**: Ollama will automatically download the llama3 model (~4.7GB). This takes a few minutes depending on your internet connection.

**Subsequent runs**: Models are persisted in a Docker volume, so they don't need to be re-downloaded.

---

### Access the Services

* **FastAPI API**: http://localhost:8000
* **API Documentation (Swagger)**: http://localhost:8000/docs
* **MLflow UI**: http://localhost:5000
* **Ollama API** (direct access): http://localhost:11434

---

## 📖 API Documentation

### Interactive Swagger UI:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🔹 API Endpoints

### `POST /generate`

Submit a text generation request.

#### Request

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain Celery in one sentence"}'
```

```json
{
  "prompt": "Explain Celery in one sentence"
}
```

#### Response

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f",
  "status": "Task submitted",
  "check_url": "/status/a72a58c5-96d4-4052-bdb8-80a923faca4f"
}
```

---

### `GET /status/{task_id}`

Retrieve task status and result.

#### Request

```bash
curl http://localhost:8000/status/a72a58c5-96d4-4052-bdb8-80a923faca4f
```

#### Response (Completed)

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f",
  "status": "SUCCESS",
  "result": {
    "model": "llama3",
    "response": "Celery is a distributed task queue used for background processing in Python applications.",
    "created_at": "2025-01-19T10:30:00.000000Z",
    "done": true,
    "total_duration": 1523456789,
    "load_duration": 12345678,
    "prompt_eval_count": 15,
    "eval_count": 42
  }
}
```

#### Response (Pending)

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f",
  "status": "PENDING",
  "result": null
}
```

#### Response (In Progress)

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f",
  "status": "PROGRESS",
  "result": {
    "current": 50,
    "total": 100
  }
}
```

#### Response (Failed)

```json
{
  "task_id": "a72a58c5-96d4-4052-bdb8-80a923faca4f",
  "status": "FAILURE",
  "error": "Connection timeout to Ollama service"
}
```

---

## 🐳 Docker Architecture

### Container Architecture

```
┌─────────────────────────────────────────────────┐
│         Docker Network (llm-network)            │
│                                                 │
│  ┌──────────┐     ┌──────────┐                 │
│  │   API    │────▶│  Worker  │                 │
│  │  :8000   │     │  (Celery)│                 │
│  └────┬─────┘     └─────┬────┘                 │
│       │                 │                       │
│       ├─────────────────┼──────────┐            │
│       │                 │          │            │
│  ┌────▼─────┐    ┌─────▼────┐  ┌──▼───────┐    │
│  │  Redis   │    │  Ollama  │  │  MLflow  │    │
│  │  :6379   │    │  :11434  │  │  :5000   │    │
│  └──────────┘    └─────┬────┘  └──────────┘    │
│                        │                        │
│                  ┌─────▼──────┐                 │
│                  │ ollama-data│ (volume)        │
│                  │  (models)  │                 │
│                  └────────────┘                 │
└─────────────────────────────────────────────────┘
```

### docker-compose.yml

```yaml
services:
  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"
    networks:
      - llm-network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - llm-network
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        ollama serve & 
        sleep 5
        ollama pull llama3
        wait
    restart: unless-stopped

  mlflow:
    build: ./mlflow
    container_name: mlflow
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow/mlruns:/mlflow/mlruns
    networks:
      - llm-network

  api:
    build: .
    container_name: llm_api
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - mlflow
      - ollama
    networks:
      - llm-network

  worker:
    build: .
    container_name: llm_worker
    command: celery -A app.celery_worker worker --pool=solo --loglevel=info
    env_file:
      - .env
    volumes:
      - ./mlflow/mlruns:/mlflow/mlruns 
    depends_on:
      - redis
      - mlflow
      - ollama
    networks:
      - llm-network

networks:
  llm-network:
    driver: bridge

volumes:
  ollama-data:
```

---

## ⚙️ Configuration

### Environment Variables

| Variable              | Description                  | Default                            |
| --------------------- | ---------------------------- | ---------------------------------- |
| `OLLAMA_URL`          | Ollama API endpoint          | `http://ollama:11434/api/generate` |
| `REDIS_URL`           | Redis connection URL         | `redis://redis:6379/0`             |
| `MLFLOW_TRACKING_URI` | MLflow server tracking URI   | `http://mlflow:5000`               |

**Note**: All URLs use internal Docker service names, not `localhost` or IP addresses.

---

## 🛠️ Development

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f worker
docker compose logs -f ollama
docker compose logs -f api
```

### Restarting Services

```bash
# Restart specific service
docker compose restart worker

# Restart everything
docker compose restart
```

### Stopping Services

```bash
# Stop all services (preserves volumes)
docker compose down

# Stop and remove volumes (deletes downloaded models!)
docker compose down -v
```

### Rebuilding After Code Changes

```bash
docker compose up --build
```

---

## 🐛 Troubleshooting

### Ollama Model Download Issues

**Problem**: First startup takes forever or fails

**Solutions**:
1. Check Ollama logs:
   ```bash
   docker compose logs ollama
   ```

2. Verify internet connection and retry:
   ```bash
   docker compose restart ollama
   ```

3. Manually pull model:
   ```bash
   docker compose exec ollama ollama pull llama3
   ```

### Worker Cannot Connect to Ollama

**Problem**: Tasks fail with connection errors

**Solutions**:
1. Verify all services are on the same network:
   ```bash
   docker network inspect llm-api_llm-network
   ```

2. Check Ollama is running:
   ```bash
   docker compose ps ollama
   ```

3. Test Ollama from worker container:
   ```bash
   docker compose exec worker curl http://ollama:11434/api/tags
   ```

### Celery Worker Fails on Windows

**Problem**: Worker crashes on startup

**Solution**: The `--pool=solo` flag is already configured in docker-compose.yml for Windows/WSL2 compatibility.

### Redis Connection Refused

**Problem**: Worker or API cannot connect to Redis

**Solutions**:
1. Check Redis is running:
   ```bash
   docker compose ps redis
   ```

2. Verify Redis logs:
   ```bash
   docker compose logs redis
   ```

### Task Stuck in PENDING

**Problem**: Tasks never complete

**Solutions**:
1. Check worker is running:
   ```bash
   docker compose ps worker
   ```

2. View worker logs for errors:
   ```bash
   docker compose logs worker
   ```

3. Verify worker can reach Ollama:
   ```bash
   docker compose exec worker ping -c 3 ollama
   ```

### MLflow UI Not Loading

**Problem**: Cannot access http://localhost:5000

**Solutions**:
1. Check MLflow container status:
   ```bash
   docker compose ps mlflow
   ```

2. View MLflow logs:
   ```bash
   docker compose logs mlflow
   ```

3. Ensure port 5000 is not in use:
   ```bash
   # Linux/Mac
   lsof -i :5000
   
   # Windows
   netstat -ano | findstr :5000
   ```

### Out of Disk Space

**Problem**: Docker runs out of space

**Solution**: Models are ~4-5GB. Clean up unused Docker resources:
```bash
docker system prune -a
docker volume prune
```

---

## 🧪 Testing the API

### Quick Test with curl

```bash
# Submit task
TASK_ID=$(curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is FastAPI?"}' | jq -r '.task_id')

echo "Task ID: $TASK_ID"

# Wait a few seconds, then check result
sleep 5
curl http://localhost:8000/status/$TASK_ID | jq
```

### Using HTTPie

```bash
# Submit task
http POST localhost:8000/generate prompt="Explain machine learning"

# Check status
http GET localhost:8000/status/TASK_ID
```

### Python Test Script

```python
import requests
import time
import json

def test_llm_api():
    # Submit generation task
    response = requests.post(
        "http://localhost:8000/generate",
        json={"prompt": "What are the benefits of containerization?"}
    )
    
    task_id = response.json()["task_id"]
    print(f"✓ Task submitted: {task_id}")
    
    # Poll for result
    print("⏳ Waiting for result...")
    while True:
        result = requests.get(f"http://localhost:8000/status/{task_id}").json()
        
        if result["status"] == "SUCCESS":
            print("✓ Task completed!")
            print("\nResponse:")
            print(result["result"]["response"])
            break
        elif result["status"] == "FAILURE":
            print(f"✗ Task failed: {result.get('error')}")
            break
        elif result["status"] == "PROGRESS":
            print(f"⏳ Progress: {result.get('result')}")
        
        time.sleep(2)

if __name__ == "__main__":
    test_llm_api()
```

---

## 🔍 Managing Ollama Models

### List Available Models

```bash
docker compose exec ollama ollama list
```

### Pull Additional Models

```bash
# Pull a different model
docker compose exec ollama ollama pull codellama

# Pull a specific version
docker compose exec ollama ollama pull llama3:13b
```

### Remove Models

```bash
docker compose exec ollama ollama rm llama3
```

### Check Model Info

```bash
docker compose exec ollama ollama show llama3
```

---

## 📊 Monitoring with MLflow

### Access MLflow UI

Navigate to http://localhost:5000

### View Experiments

1. Click on **Experiments** → **llm_inference**
2. See all inference runs with:
   - Prompts used
   - Latency metrics
   - Model parameters
   - Response artifacts

### Compare Runs

1. Select multiple runs
2. Click **Compare**
3. Analyze performance differences

---

## 🛠️ Project Status

| Feature                                      | Status |
| -------------------------------------------- | ------ |
| Async FastAPI API                            | ✅      |
| Celery + Redis background processing         | ✅      |
| Docker Compose multi-container orchestration | ✅      |
| Containerized Ollama with auto model pull    | ✅      |
| Persistent model storage                     | ✅      |
| Internal Docker networking                   | ✅      |
| Windows/WSL2-compatible configuration        | ✅      |
| Centralized configuration with `.env`        | ✅      |
| MLOps-ready architecture with MLflow         | ✅      |
| Task status tracking and polling             | ✅      |

---

## 🔮 Planned Enhancements

* [ ] **GPU support** for Ollama container
* [ ] **Multiple model support** (select model per request)
* [ ] **Hugging Face model registry** integration
* [ ] **Authentication** and rate limiting
* [ ] **Streaming responses** support
* [ ] **Health check endpoints** for all services
* [ ] **Request caching** with Redis
* [ ] **Batch processing** capabilities
* [ ] **Prometheus metrics** export
* [ ] **Grafana dashboards**
* [ ] **Auto-scaling** worker containers
* [ ] **Request queuing** with priority levels

---

## 📌 Architecture Benefits

### Complete Containerization
- **Zero host dependencies**: Everything runs in Docker
- **Consistent environments**: Same setup on dev, staging, prod
- **Easy deployment**: Single `docker compose up` command
- **Portable**: Works on any Docker-capable system

### Automatic Model Management
- **Auto-download**: Models pulled on first startup
- **Persistence**: Models stored in Docker volumes
- **Version control**: Pin specific model versions
- **Easy updates**: Pull new models without rebuilding

### Service Isolation
- **Dedicated network**: Services communicate securely
- **Resource limits**: Set CPU/memory constraints per service
- **Independent scaling**: Scale services independently
- **Fault isolation**: Service failures don't cascade

### Developer Experience
- **Fast onboarding**: No complex local setup
- **Reproducible**: Same environment for all developers
- **Easy debugging**: Individual container logs
- **Hot reload**: Code changes reflected without full rebuild

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Docker Hub](https://hub.docker.com/r/ollama/ollama)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👤 Author

**Yahia Achouri**

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

## ⭐ Show your support

Give a ⭐️ if this project helped you learn about building production-ready LLM APIs with full containerization!
