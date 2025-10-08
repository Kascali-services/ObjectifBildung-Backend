import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "GatewayService")
    APP_PORT: int = os.getenv("APP_PORT", 8080)
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://authservice:5001")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_DB: int = os.getenv("REDIS_DB", 0)
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")  # 10 req/minute par IP
    ENV: str = os.getenv("ENV", "development")

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignore les variables non listées au lieu d’échouer


settings = Settings()
