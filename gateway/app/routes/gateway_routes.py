from fastapi import APIRouter, Request, Depends

from app.core.config import settings
from app.services.auth_service import proxy_to_auth
from app.core.limiter import limiter

gateway_router = APIRouter(prefix="/gateway", tags=["Gateway"])

@gateway_router.post("/auth/{path:path}")
@limiter.limit(settings.RATE_LIMIT)
async def proxy_auth_request(path: str, request: Request):
    data = await request.json()
    headers = dict(request.headers)
    response = await proxy_to_auth(f"/{path}", "POST", data, headers)
    return response.json()
