# app/routes/auth_router.py (ou où tu définis tes routes)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.contoller.user_controller import get_user_by_email, create_user, generate_token_for_user, authenticate_user, \
    set_reset_token
from app.db.database import get_db
from app.schemas import UserCreate, UserLogin, TokenResponse, ForgotPasswordRequest
from sqlalchemy.exc import SQLAlchemyError

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=TokenResponse)
def register(request: UserCreate, db: Session = Depends(get_db)):
    try:
        # Sanitize / normaliser l'email
        email = str(request.email).strip().lower()
        if get_user_by_email(db, email):
            # Ne pas donner trop d'infos, message générique
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = create_user(db, email, request.password)
        token = generate_token_for_user(user)
        return TokenResponse(access_token=token)
    except ValueError as ve:
        # Erreur de validation (ex: password policy)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except SQLAlchemyError:
        # Erreur côté DB
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


@auth_router.post("/login", response_model=TokenResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    try:
        email = str(request.email).strip().lower()
        user = authenticate_user(db, email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = generate_token_for_user(user)
        return TokenResponse(access_token=token)

    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except Exception as e:
        print("Unexpected error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@auth_router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = str(request.email).strip().lower()
        token = set_reset_token(db, email)
        if not token:
            # Pas d'indication si user n'existe pas — on renvoie un message générique
            # pour éviter le user enumeration; si tu veux informer, return 200 sans token.
            return {"message": "If an account with this email exists, a reset link has been sent."}
        # Ici normalement envoie d'email asynchrone (celery, background task)
        # On ne doit PAS renvoyer le token dans la réponse en prod.
        # Pour le dev on peut renvoyer : token (mais attention en prod)
        return {"message": "Password reset link sent (development)", "reset_token": token}
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
