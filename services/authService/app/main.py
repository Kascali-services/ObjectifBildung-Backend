from fastapi import FastAPI

from app.auth_routes import auth_router
from app.config import dev_config
from app.db.database import Base, engine


def create_app() -> FastAPI:
    auth_app = FastAPI(
        title=dev_config.PROJECT_NAME,
        version=dev_config.VERSION,
        description="Authentication microservice for ObjectifBildung"
    )
    Base.metadata.create_all(bind=engine)
    auth_app.include_router(auth_router)

    @auth_app.get("/health")
    def health():
        return {"status": "ok"}

    return auth_app


app = create_app()
