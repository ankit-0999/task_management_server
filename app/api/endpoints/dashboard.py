from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import func

from app.api import deps
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.models.enums import UserRole, TaskStatus, ProjectStatus

router = APIRouter()


class DashboardStats:
    """Response model for dashboard statistics"""
    def __init__(self):
        self.total_tasks = 0
        self.todo_tasks = 0
        self.in_progress_tasks = 0
        self.completed_tasks = 0
        self.overdue_tasks = 0
        self.total_projects = 0
        self.active_projects = 0
        self.completed_projects = 0


@router.get("/member", response_model=dict)
def get_member_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get dashboard data for a Member"""
    try:
        if current_user.role != UserRole.MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint is for members only"
            )

        # Get member's assigned tasks
        assigned_tasks = db.query(Task).filter(
            Task.assignee_id == current_user.id
        ).all()

        # Get task statistics
        total_tasks = len(assigned_tasks)
        todo_tasks = len([t for t in assigned_tasks if t.status == "Todo"])
        in_progress_tasks = len([t for t in assigned_tasks if t.status == "In-Progress"])
        completed_tasks = len([t for t in assigned_tasks if t.status == "Completed"])
        
        # Get overdue tasks (due_date is past and status is not Completed)
        now = datetime.utcnow()
        overdue_tasks = len([
            t for t in assigned_tasks 
            if t.due_date and t.due_date < now and t.status != "Completed"
        ])

        # Get member's projects (through joined_projects relationship)
        total_projects = len(current_user.joined_projects) if current_user.joined_projects else 0
        
        # Get projects statistics
        active_projects = len([
            p for p in (current_user.joined_projects or [])
            if p.status in ["Todo", "In-Progress"]
        ]) if current_user.joined_projects else 0
        
        completed_projects = len([
            p for p in (current_user.joined_projects or [])
            if p.status == "Completed"
        ]) if current_user.joined_projects else 0

        # Get recent tasks (last 5)
        recent_tasks = sorted(
            assigned_tasks,
            key=lambda t: t.created_at or datetime.min,
            reverse=True
        )[:5]

        return {
            "stats": {
                "total_tasks": total_tasks,
                "todo_tasks": todo_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
            },
            "recent_tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "due_date": t.due_date,
                    "project_id": t.project_id,
                }
                for t in recent_tasks
            ],
            "projects": [
                {
                    "id": p.id,
                    "title": p.title,
                    "status": p.status,
                }
                for p in (current_user.joined_projects or [])
            ]
        }
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")


@router.get("/admin", response_model=dict)
def get_admin_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_admin),
) -> Any:
    """Get dashboard data for an Admin"""
    try:
        # Get admin's projects
        admin_projects = db.query(Project).filter(
            Project.owner_id == current_user.id
        ).all()

        total_projects = len(admin_projects)
        active_projects = len([
            p for p in admin_projects
            if p.status in ["Todo", "In-Progress"]
        ])
        completed_projects = len([
            p for p in admin_projects
            if p.status == "Completed"
        ])

        # Get all tasks in admin's projects
        project_ids = [p.id for p in admin_projects]
        all_tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all() if project_ids else []

        total_tasks = len(all_tasks)
        todo_tasks = len([t for t in all_tasks if t.status == "Todo"])
        in_progress_tasks = len([t for t in all_tasks if t.status == "In-Progress"])
        completed_tasks = len([t for t in all_tasks if t.status == "Completed"])

        # Get overdue tasks
        now = datetime.utcnow()
        overdue_tasks = len([
            t for t in all_tasks
            if t.due_date and t.due_date < now and t.status != "Completed"
        ])

        # Get team members count
        team_members_set = set()
        for project in admin_projects:
            if project.members:
                team_members_set.update([m.id for m in project.members])
        team_members_count = len(team_members_set)

        return {
            "stats": {
                "total_tasks": total_tasks,
                "todo_tasks": todo_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "team_members": team_members_count,
            },
            "projects": [
                {
                    "id": p.id,
                    "title": p.title,
                    "status": p.status,
                    "task_count": len([t for t in all_tasks if t.project_id == p.id]),
                }
                for p in admin_projects
            ],
            "recent_tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "assignee_id": t.assignee_id,
                    "due_date": t.due_date,
                }
                for t in sorted(all_tasks, key=lambda t: t.created_at or datetime.min, reverse=True)[:5]
            ]
        }
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")
