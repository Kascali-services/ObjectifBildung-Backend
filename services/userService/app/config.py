import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "UserService")
    VERSION: str = os.getenv("VERSION", "0.1.0")

class DevConfig(Config):
    DATABASE_URL: str = os.getenv("DEV_DATABASE_URL", "sqlite:///./user.db")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "fr")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

dev_config = DevConfig()
