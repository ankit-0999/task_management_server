import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

project_members = Table(
    "project_members",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String, default="Todo")
    start_date = Column(DateTime, nullable=True)
    estimation_date = Column(DateTime, nullable=True)
    closed_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    members = relationship("User", secondary=project_members, back_populates="joined_projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
