"""NotificationPreference model for user notification settings."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid


class NotificationPreference(SQLModel, table=True):
    """User notification preferences."""
    __tablename__ = "notification_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)

    # Channel preferences
    web_push_enabled: bool = Field(default=True)
    email_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)

    # Timing preferences
    quiet_hours_start: Optional[int] = Field(default=None, ge=0, le=23)
    quiet_hours_end: Optional[int] = Field(default=None, ge=0, le=23)
    timezone: str = Field(default="UTC", max_length=50)

    # Default reminder timing
    default_reminder_minutes: int = Field(default=60, ge=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationPreferencePublic(SQLModel):
    """Public notification preference model."""
    id: int
    user_id: uuid.UUID
    web_push_enabled: bool
    email_enabled: bool
    in_app_enabled: bool
    quiet_hours_start: Optional[int]
    quiet_hours_end: Optional[int]
    timezone: str
    default_reminder_minutes: int
