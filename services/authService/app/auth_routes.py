from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.contoller.user_controller import get_user_by_email, create_user, generate_token_for_user, authenticate_user, \
    set_reset_token

from app.db.database import get_db
from app.schemas import UserCreate, UserLogin, TokenResponse, ForgotPasswordRequest

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=TokenResponse)
def register(request: UserCreate, db: Session = Depends(get_db)):
    # print("Password type:", type(request.password), "Value:", request.password)
    if get_user_by_email(db, str(request.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, str(request.email), request.password)
    token = generate_token_for_user(user)
    return TokenResponse(access_token=token)


@auth_router.post("/login", response_model=TokenResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, str(request.email), request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = generate_token_for_user(user)
    return TokenResponse(access_token=token)


@auth_router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token = set_reset_token(db, str(request.email))
    if not token:
        raise HTTPException(status_code=404, detail="User not found")
    # Simule l'envoi d'email (tu pourras ajouter Mailgun/SMTP ici)
    return {"message": "Password reset link sent", "reset_token": token}
