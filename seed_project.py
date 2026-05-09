import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.user import User

db = SessionLocal()

try:
    user = db.query(User).first()
    if not user:
        print("No user found in the database. Please sign up on the frontend first.")
        sys.exit(1)

    project = db.query(Project).first()
    if not project:
        project = Project(
            title="Frontend Development", 
            description="Default project for demo purposes", 
            owner_id=user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Successfully created Default Project (ID: {project.id})!")
    else:
        print("Project 1 already exists.")
finally:
    db.close()
