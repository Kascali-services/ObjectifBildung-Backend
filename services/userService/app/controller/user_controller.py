from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db.user_models import User


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_auth_id(db: Session, auth_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.auth_id == auth_id).first()

def create_user_profile(db: Session, user_data: dict) -> User:
    if get_user_by_auth_id(db, user_data["auth_id"]):
        raise ValueError("User profile already exists")

    user = User(**user_data)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

def update_user_profile(db: Session, user_id: UUID, updates: dict) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in updates.items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

def is_profile_complete(user: User) -> bool:
    return all([
        user.first_name,
        user.last_name,
        user.country,
        user.city
    ])
