import httpx
from app.core.config import settings

async def proxy_to_auth(path: str, method: str = "GET", data=None, headers=None):
    url = f"{settings.AUTH_SERVICE_URL}/auth{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data, headers=headers)
    return response
