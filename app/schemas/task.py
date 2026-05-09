from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: str
    assignee_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    project_id: str
    assignee_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
