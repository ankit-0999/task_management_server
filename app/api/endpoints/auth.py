from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    try:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
        user = User(
            email=user_in.email,
            name=user_in.name,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.post("/login/access-token")
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_json(
    request: LoginRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    JSON Login (Disha style)
    """
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")
