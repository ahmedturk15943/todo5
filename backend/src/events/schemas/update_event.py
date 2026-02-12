"""Update event schema for real-time synchronization."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import Field
import uuid

from .base import BaseEvent


class UpdateEvent(BaseEvent):
    """Event for real-time task updates across devices.

    Published to task-updates topic for WebSocket broadcasting.
    """

    event_type: str = Field(
        ...,
        description="Type of update: task.created, task.updated, task.deleted, task.completed"
    )
    task_id: uuid.UUID = Field(..., description="ID of the affected task")
    user_id: uuid.UUID = Field(..., description="ID of the user who owns the task")
    changes: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary of changed fields (for updates)"
    )
    task_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Full task data (for creates and major updates)"
    )
    version: Optional[int] = Field(
        None,
        description="Task version for optimistic locking"
    )
    source_device_id: Optional[str] = Field(
        None,
        description="Device ID that originated the change (to avoid echo)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "task.updated",
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43f7-8d9e-123456789abc",
                "timestamp": "2025-01-15T10:30:00Z",
                "changes": {
                    "title": "Updated task title",
                    "status": "complete"
                },
                "version": 5,
                "source_device_id": "device-abc-123"
            }
        }
