# app/controllers/user_controller.py
from sqlalchemy.orm import Session
from app.db import models
from app.security import hash_password, verify_password, create_access_token, generate_reset_token, check_password_policy
from typing import Optional
from datetime import datetime, timedelta
from app.config import dev_config as settings

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str) -> models.User:
    # validation de base
    ok, msg = check_password_policy(password)
    if not ok:
        raise ValueError(msg)

    if get_user_by_email(db, email):
        raise ValueError("Email already registered")

    hashed = hash_password(password)
    user = models.User(email=email, hashed_password=hashed)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    # verify_password returns boolean safely
    if not verify_password(password, user.hashed_password):
        return None
    return user

def generate_token_for_user(user: models.User) -> str:
    # charge utile minimale (sub = email)
    payload = {"sub": user.email}
    return create_access_token(payload)

def set_reset_token(db: Session, email: str) -> Optional[str]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    token = generate_reset_token()
    # define expiration time (ex: 1 heure)
    expires = datetime.utcnow() + timedelta(hours=getattr(settings, "RESET_TOKEN_EXPIRE_HOURS", 1))
    # check if field exist
    user.reset_token = token
    user.reset_token_expires = expires
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return token
    except Exception:
        db.rollback()
        raise
