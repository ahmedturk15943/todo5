"""ActivityLog model for tracking task operations."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum


class ActivityAction(str, Enum):
    """Activity action types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"
    DELETED = "deleted"
    RESTORED = "restored"


class ActivityLog(SQLModel, table=True):
    """Activity log for audit trail."""

    __tablename__ = "activity_logs"

    id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", index=True)
    action: ActivityAction = Field(index=True)
    entity_type: str = Field(default="task", index=True)
    entity_id: Optional[int] = Field(default=None, index=True)
    changes: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": 42,
                "action": "updated",
                "entity_type": "task",
                "entity_id": 42,
                "changes": {
                    "title": {"old": "Old title", "new": "New title"},
                    "status": {"old": "incomplete", "new": "complete"}
                },
                "metadata": {
                    "device_id": "device-123",
                    "source": "web"
                },
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class ActivityLogPublic(SQLModel):
    """Public activity log schema."""

    id: int
    user_id: uuid.UUID
    task_id: Optional[int]
    action: ActivityAction
    entity_type: str
    entity_id: Optional[int]
    changes: Optional[dict]
    metadata: Optional[dict]
    created_at: datetime
