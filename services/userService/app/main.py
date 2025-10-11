from fastapi import FastAPI
from app.routes.user_routes import router
from app.config import dev_config
from app.db.database import Base, engine

def create_app() -> FastAPI:
    user_app = FastAPI(
        title=dev_config.PROJECT_NAME,
        version=dev_config.VERSION,
        description="User profile microservice for ObjectifBildung"
    )

    Base.metadata.create_all(bind=engine)
    user_app.include_router(router)

    @user_app.get("/health")
    def health():
        return {"status": "ok"}

    return user_app

app = create_app()
