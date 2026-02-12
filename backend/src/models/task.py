"""Task model for todo items."""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import TSVECTOR
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class PriorityLevel(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task completion status."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class Task(SQLModel, table=True):
    """Task entity belonging to a user."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Phase 5: New fields
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE, index=True)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)

    # Recurring task support
    recurring_pattern_id: Optional[int] = Field(default=None, foreign_key="recurring_patterns.id")
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Optimistic locking
    version: int = Field(default=1)

    # Full-text search (auto-updated via trigger)
    search_vector: Optional[str] = Field(default=None, sa_column=Column(TSVECTOR))

    # Relationships
    recurring_pattern: Optional["RecurringPattern"] = Relationship(back_populates="tasks")
    reminders: List["Reminder"] = Relationship(back_populates="task", cascade_delete=True)
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    activity_logs: List["ActivityLog"] = Relationship(back_populates="task", cascade_delete=True)
    child_tasks: List["Task"] = Relationship(
        back_populates="parent_task",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    parent_task: Optional["Task"] = Relationship(back_populates="child_tasks")


class TaskPublic(SQLModel):
    """Public task model for API responses."""
    id: int
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: PriorityLevel
    due_date: Optional[datetime]
    recurring_pattern_id: Optional[int]
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    version: int


class TaskCreate(SQLModel):
    """Model for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    due_date: Optional[datetime] = None
    recurring_pattern_id: Optional[int] = None


class TaskUpdate(SQLModel):
    """Model for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
