import httpx
from app.core.config import settings

async def proxy_to_auth(path: str, method: str, data, headers: dict):
    url = f"{settings.AUTH_SERVICE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient() as client:
        if data:
            response = await client.request(method, url, content=data, headers=headers)
        else:
            response = await client.request(method, url, headers=headers)
    return response
