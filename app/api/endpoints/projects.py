from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.api import deps
from app.models.project import Project
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    try:
        if current_user.role == UserRole.ADMIN:
            # Admins see projects they own
            projects = db.query(Project).filter(Project.owner_id == current_user.id).offset(skip).limit(limit).all()
        else:
            # Members see projects they are assigned to
            projects = current_user.joined_projects
        return projects
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.post("/", response_model=ProjectResponse)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions. Only admins can create projects.")

    try:
        project = Project(
            title=project_in.title,
            description=project_in.description,
            owner_id=current_user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

@router.post("/{project_id}/members/{user_id}")
def add_member(
    project_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role != UserRole.ADMIN or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to add members.")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user not in project.members:
        project.members.append(user)
        db.commit()
        
    return {"status": "success", "detail": f"User {user.name} added to project {project.title}"}

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role != UserRole.ADMIN or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to edit this project.")
        
    project.title = project_in.title
    project.description = project_in.description
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role != UserRole.ADMIN or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this project.")
        
    db.delete(project)
    db.commit()
    return {"status": "success", "detail": "Project deleted successfully"}
