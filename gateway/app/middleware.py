from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from app.core.redis_client import redis_client
import json

class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)

        cache_key = f"cache:{request.url.path}?{request.url.query}"
        cached = redis_client.get(cache_key)
        if cached:
            return JSONResponse(content=json.loads(cached))

        response = await call_next(request)
        if response.status_code == 200:
            body = await response.body()
            redis_client.setex(cache_key, 60, body.decode())
        return response
