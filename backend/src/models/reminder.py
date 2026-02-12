"""Reminder model for scheduled task notifications."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ReminderStatus(str, Enum):
    """Reminder delivery status."""
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Reminder(SQLModel, table=True):
    """Scheduled reminder for a task."""
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Scheduling
    remind_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Delivery tracking
    status: ReminderStatus = Field(default=ReminderStatus.PENDING, index=True)
    sent_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Dapr Jobs API integration
    job_id: Optional[str] = Field(default=None, unique=True)

    # Relationships
    task: "Task" = Relationship(back_populates="reminders")


class ReminderCreate(SQLModel):
    """Model for creating a reminder."""
    task_id: int
    remind_at: datetime


class ReminderPublic(SQLModel):
    """Public reminder model for API responses."""
    id: int
    task_id: int
    user_id: uuid.UUID
    remind_at: datetime
    created_at: datetime
    status: ReminderStatus
    sent_at: Optional[datetime]
    job_id: Optional[str]
