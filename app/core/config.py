from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    REDIS_URL: str = "redis://localhost:6379/0"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    class Config:
        env_file = ".env"

settings = Settings()
