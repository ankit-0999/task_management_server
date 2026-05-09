from fastapi import APIRouter
from app.api.endpoints import tasks, auth, projects, users

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
