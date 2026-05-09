from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.api import deps
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve users (used for assigning tasks).
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")
