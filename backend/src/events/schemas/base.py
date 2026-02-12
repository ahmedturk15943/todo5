"""Base event schema classes for event-driven architecture."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Literal, Optional


class BaseEvent(BaseModel):
    """Base event schema with common fields."""

    schema_version: str = Field(default="1.0", description="Event schema version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskEventType(str):
    """Task event types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    REOPENED = "reopened"
    DELETED = "deleted"


class ReminderEventType(str):
    """Reminder event types."""
    SCHEDULED = "reminder.scheduled"
    DUE = "reminder.due"
    SENT = "reminder.sent"
    CANCELLED = "reminder.cancelled"
    FAILED = "reminder.failed"


class UpdateEventType(str):
    """Real-time update event types."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    TAG_ADDED = "tag.added"
    TAG_REMOVED = "tag.removed"
