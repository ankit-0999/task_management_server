from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.api import deps
from app.models.task import Task
from app.models.project import Project
from app.models.enums import UserRole, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    project_id: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    try:
        query = db.query(Task)
        
        # RBAC Read logic
        if current_user.role == UserRole.MEMBER:
            # Members can only see their specifically assigned tasks
            query = query.filter(Task.assignee_id == current_user.id)
            
        if status:
            query = query.filter(Task.status == status)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        
        tasks = query.offset(skip).limit(limit).all()
        return tasks
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.post("/", response_model=TaskResponse)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions. Only admins can create tasks.")
        
    try:
        task = Task(
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            due_date=task_in.due_date,
            start_date=task_in.start_date,
            estimation_date=task_in.estimation_date,
            closed_date=task_in.closed_date,
            project_id=task_in.project_id,
            assignee_id=task_in.assignee_id if task_in.assignee_id else None
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task Not Found")

        if current_user.role == UserRole.MEMBER:
            # Check if current_user.id == task.assignee_id
            if task.assignee_id != current_user.id:
                raise HTTPException(status_code=403, detail="Forbidden. You can only update your own assigned tasks.")
                
            # If yes, ONLY allow updates to status. We ignore other fields since the frontend
            # form may submit them as read-only values.
            if task_in.status:
                task.status = task_in.status
            db.commit()
            db.refresh(task)
            return task

        # Admins can update any fields
        update_data = task_in.dict(exclude_unset=True)
        if 'assignee_id' in update_data and not update_data['assignee_id']:
            update_data['assignee_id'] = None

        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.delete("/{task_id}")
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: str,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task Not Found")
        
        db.delete(task)
        db.commit()
        return {"status": "success", "detail": "Task deleted successfully"}
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")
