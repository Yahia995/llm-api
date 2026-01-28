from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"
    REDIS_URL: str = "redis://localhost:6379/0"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    DATABASE_URL: str = ""  # Neon Postgres connection string

    class Config:
        env_file = ".env"

settings = Settings()
