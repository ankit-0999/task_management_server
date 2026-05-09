from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.enums import ProjectStatus

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.TODO
    start_date: Optional[datetime] = None
    estimation_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None

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
