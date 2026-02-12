"""Reminder event schema."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

from .base import BaseEvent


class ReminderEvent(BaseEvent):
    """Reminder event schema for reminders topic."""

    event_type: Literal["reminder.scheduled", "reminder.due", "reminder.sent", "reminder.cancelled", "reminder.failed"]
    reminder_id: int
    task_id: int
    user_id: str
    remind_at: str = Field(description="ISO format datetime")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "schema_version": "1.0",
                "event_type": "reminder.due",
                "reminder_id": 456,
                "task_id": 123,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "remind_at": "2026-02-12T09:00:00Z",
                "timestamp": "2026-02-12T09:00:00Z",
                "metadata": {}
            }
        }
