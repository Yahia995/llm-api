from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    REDIS_URL: str = "redis://localhost:6379/0"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    DATABASE_URL: str = ""

    @property
    def redis_url_safe(self) -> str:
        url = self.REDIS_URL
        if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}ssl_cert_reqs=CERT_NONE"
        return url

    class Config:
        env_file = ".env"


settings = Settings()
