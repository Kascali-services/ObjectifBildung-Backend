from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.redis_client import redis_client

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{redis_client.connection_pool.connection_kwargs['host']}:6379"
)
