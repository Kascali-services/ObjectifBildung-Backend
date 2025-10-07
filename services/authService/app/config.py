import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "MyProject")
    VERSION: str = os.getenv("VERSION", "0.1.0")


class DevConfig(Config):
    SECRET_KEY: str = os.getenv("DEV_SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    DATABASE_URL: str = os.getenv("DEV_DATABASE_URL", "sqlite:///./auth.db")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


dev_config = DevConfig()
