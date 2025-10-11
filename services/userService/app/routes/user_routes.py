from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.controller.user_controller import (
    get_user_by_id,
    get_user_by_auth_id,
    create_user_profile,
    update_user_profile,
    is_profile_complete
)
from app.schema import UserResponse, UserUpdate, ProfileStatus
from app.schemas import UserCreate

router = APIRouter(prefix="/users", tags=["User Profile"])


@router.post("/", response_model=UserResponse)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_auth_id(db, request.auth_id)
    if existing:
        raise HTTPException(status_code=400, detail="User profile already exists")
    user = create_user_profile(db, request.dict())
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, request: UserUpdate, db: Session = Depends(get_db)):
    updated = update_user_profile(db, user_id, request.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.get("/{user_id}/status", response_model=ProfileStatus)
def check_profile_status(user_id: UUID, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileStatus(is_complete=is_profile_complete(user))
