from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    owner_id: Optional[str] = None # Will be set by backend

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
