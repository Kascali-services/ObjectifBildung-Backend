# app/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional, Tuple
import re
import secrets
from app.config import dev_config as settings

# CryptContext with Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ----- Password hashing / verification -----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # passlib already uses safe comparisons
    return pwd_context.verify(plain_password, hashed_password)


# ----- Token creation & verification -----
def _create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict) -> str:
    # refresh longer lived (configurable)
    return _create_token(data, timedelta(days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)))


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise


# ----- Reset token (non-jwt, random token) -----
def generate_reset_token(length: int = 48) -> str:
    # cryptographically secure random token
    return secrets.token_urlsafe(length)


# ----- Password policy -----
def check_password_policy(password: str) -> tuple[bool, str | None]:
    """
    Validates that the password complies with the security policy:
    - Minimum length of 8 characters
    - Optional: must include uppercase, lowercase, digit
    - Allow common special characters for security
    """

    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Interdire uniquement les caractères problématiques pour la DB ou injection
    forbidden_chars = "';--\\"
    if any(char in forbidden_chars for char in password):
        return False, f"Password must not contain characters like {forbidden_chars}"

    # Optional: uncomment for stricter checks
    # import re
    # if not re.search(r"[A-Z]", password):
    #     return False, "Password must contain at least one uppercase letter."
    # if not re.search(r"[a-z]", password):
    #     return False, "Password must contain at least one lowercase letter."
    # if not re.search(r"[0-9]", password):
    #     return False, "Password must contain at least one digit."

    return True, None


"""from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse

class GatewayOnlyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Vérifie si le header custom est présent
        gateway_token = request.headers.get("X-Gateway-Token")
        if gateway_token != "objectifbildung-secure":
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied. Requests must go through Gateway."}
            )
        return await call_next(request)"""
