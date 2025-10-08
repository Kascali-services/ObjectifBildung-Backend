# app/security.py
from datetime import datetime, timedelta
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
def _create_token(data: dict, expires_delta: Optional[timedelta]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
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
def check_password_policy(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the password complies with the security policy:
    - Minimum length of 8 characters
    - No special characters (to prevent injection)
    - Optional: at least one uppercase, lowercase, and digit

    Returns (True, None) if valid, otherwise (False, error message).
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if any(char in "!@#$\",.<>/?\\" for char in password):
        return False, "Password must not contain special characters like %^&*()_+-=[]{}|;':"

    # Optional checks — uncomment if needed
    # import re
    # if not re.search(r"[A-Z]", password):
    #     return False, "Password must contain at least one uppercase letter."
    # if not re.search(r"[a-z]", password):
    #     return False, "Password must contain at least one lowercase letter."
    # if not re.search(r"[0-9]", password):
    #     return False, "Password must contain at least one digit."

    return True, None
