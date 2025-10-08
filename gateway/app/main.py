from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.routes.gateway_routes import gateway_router
from app.middleware import CacheMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="Gateway Service")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: e.response)

app.add_middleware(BaseHTTPMiddleware, dispatch=CacheMiddleware().dispatch)
app.include_router(gateway_router)
