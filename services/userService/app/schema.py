from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# Création de profil (appelé par AuthService ou Kafka)
class UserCreate(BaseModel):
    auth_id: UUID  # UUID généré par AuthService
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    language: Optional[str] = "fr"

# Mise à jour du profil
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    language: Optional[str] = None

# Réponse complète
class UserResponse(UserCreate):
    id: UUID
    is_active: bool

    class Config:
        orm_mode = True

# Vérification de complétion
class ProfileStatus(BaseModel):
    is_complete: bool
