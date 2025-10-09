from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.routes.gateway_routes import gateway_router
from app.middleware import CacheMiddleware

app = FastAPI(title="Gateway Service")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: e.response)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CacheMiddleware)
app.include_router(gateway_router)


@app.on_event("startup")
async def startup_event():
    print(f" {settings.APP_NAME} running on port {settings.APP_PORT}")
    print(f" Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f" Auth Service: {settings.AUTH_SERVICE_URL}")
