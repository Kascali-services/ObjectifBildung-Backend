from fastapi import FastAPI

from services.authService.app.config import dev_config


def create_app() -> FastAPI:
    auth_app = FastAPI(
        title=dev_config.PROJECT_NAME,
        version=dev_config.VERSION,
        description="Authentication microservice for ObjectifBildung"
    )

    return auth_app


app = create_app()
