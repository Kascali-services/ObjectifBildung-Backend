from sqlalchemy.orm import Session
from app.db import models
from app.security import hash_password, verify_password, create_access_token
import secrets

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str):
    hashed = hash_password(password)
    user = models.User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def generate_token_for_user(user: models.User):
    return create_access_token({"sub": user.email})

def set_reset_token(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    db.commit()
    db.refresh(user)
    return token
