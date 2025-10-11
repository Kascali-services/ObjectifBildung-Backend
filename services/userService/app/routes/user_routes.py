from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.controller.user_controller import (
    get_user_by_id,
    get_user_by_auth_id,
    create_user_profile,
    update_user_profile,
    is_profile_complete,
)
from app.schema import UserResponse, UserCreate, UserUpdate, ProfileStatus

router = APIRouter(prefix="/users", tags=["User Profile"])


# ==============================================================
# Create a new user profile
# ==============================================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user profile linked to an auth_id.
    Called after a successful registration in AuthService.
    """
    existing = get_user_by_auth_id(db, request.auth_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile already exists."
        )

    user = create_user_profile(db, request.dict())
    return user


# ==============================================================
# Get a user by UUID
# ==============================================================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a user profile by ID.
    This endpoint will be protected by the Gateway JWT middleware.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user


# ==============================================================
# Update user profile
# ==============================================================
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, request: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's profile information.
    The Gateway will verify token and user permissions before calling this.
    """
    updated_user = update_user_profile(db, user_id, request.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return updated_user


# ==============================================================
# Check profile completeness
# ==============================================================
@router.get("/{user_id}/status", response_model=ProfileStatus)
def check_profile_status(user_id: UUID, db: Session = Depends(get_db)):
    """
    Check if a user profile is complete.
    This can be used to guide onboarding steps in the frontend.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return ProfileStatus(is_complete=is_profile_complete(user))
