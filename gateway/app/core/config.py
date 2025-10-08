import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://authservice:8000")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB: int = os.getenv("REDIS_DB", 0)
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")  # 10 req/minute par IP
    ENV: str = os.getenv("ENV", "development")

    class Config:
        env_file = ".env"


settings = Settings()
