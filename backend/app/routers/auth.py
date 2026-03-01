from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models.models import User, UserRole
from ..schemas.schemas import UserCreate, UserOut
from ..utils.auth import get_password_hash

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if not settings.OPEN_REGISTRATION:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    # unique checks
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already in use")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        department=user_in.department,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.end_user,  # keep it safe
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/registration-enabled")
def registration_enabled():
    return {"enabled": bool(settings.OPEN_REGISTRATION)}
