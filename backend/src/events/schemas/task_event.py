"""Task event schema for event-driven architecture."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Literal

from .base import BaseEvent


class TaskEvent(BaseEvent):
    """Task event schema for task-events topic."""

    event_type: Literal["created", "updated", "completed", "reopened", "deleted"]
    task_id: int
    user_id: str
    task_data: Dict[str, Any] = Field(description="Full task object")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "schema_version": "1.0",
                "event_type": "completed",
                "task_id": 123,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-02-12T10:30:00Z",
                "task_data": {
                    "id": 123,
                    "title": "Daily standup",
                    "status": "complete",
                    "recurring_pattern_id": 5
                },
                "metadata": {}
            }
        }
