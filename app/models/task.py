import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import TaskStatus

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(
        Enum(
            TaskStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=True,
        ),
        default=TaskStatus.TODO,
        nullable=False,
    )
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    estimation_date = Column(DateTime(timezone=True), nullable=True)
    closed_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")

    @property
    def assigneeName(self):
        return self.assignee.name if self.assignee else None

    @property
    def projectName(self):
        return self.project.title if self.project else None
