from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.util.preloaded import engine_url

from services.authService.app.config import dev_config

SQLALCHEMY_DATABASE_URL = dev_config.DATABASE_URL

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
