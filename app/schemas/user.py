from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.MEMBER

class UserResponse(UserBase):
    id: str
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
