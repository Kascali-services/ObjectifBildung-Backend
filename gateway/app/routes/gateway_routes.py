from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.services.auth_service import proxy_to_auth
from app.core.limiter import limiter

gateway_router = APIRouter(prefix="/gateway", tags=["Gateway"])

@gateway_router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@limiter.limit(settings.RATE_LIMIT)
async def proxy_auth_request(path: str, request: Request):
    # Read body if needed
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
    else:
        body = None

    # Clean headers (avoid content-length mismatch)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "content-length"}

    # Proxy to AuthService
    response = await proxy_to_auth(f"/auth/{path}", request.method, body, headers)

    # Read content
    content = await response.aread()

    # Return full response with status code and headers
    return Response(
        content=content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type")
    )
