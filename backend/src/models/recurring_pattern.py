"""RecurringPattern model for task recurrence definitions."""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RecurrenceEndType(str, Enum):
    """How recurrence ends."""
    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    BY_DATE = "by_date"


class RecurringPattern(SQLModel, table=True):
    """Recurring task pattern definition."""
    __tablename__ = "recurring_patterns"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Recurrence definition
    frequency: RecurrenceFrequency = Field(index=True)
    interval: int = Field(default=1, ge=1)
    start_date: datetime = Field(index=True)

    # Weekly: specific days (e.g., [0, 2, 4] for Mon, Wed, Fri)
    weekly_days: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))

    # Monthly: specific date (e.g., 15 for 15th of each month)
    monthly_day: Optional[int] = Field(default=None, ge=1, le=31)

    # End condition
    end_type: RecurrenceEndType = Field(default=RecurrenceEndType.NEVER)
    end_date: Optional[datetime] = Field(default=None)
    max_occurrences: Optional[int] = Field(default=None, ge=1)
    current_occurrence: int = Field(default=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="recurring_pattern")


class RecurringPatternCreate(SQLModel):
    """Model for creating a recurring pattern."""
    frequency: RecurrenceFrequency
    interval: int = Field(default=1, ge=1)
    start_date: datetime
    weekly_days: Optional[List[int]] = None
    monthly_day: Optional[int] = Field(default=None, ge=1, le=31)
    end_type: RecurrenceEndType = Field(default=RecurrenceEndType.NEVER)
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = Field(default=None, ge=1)


class RecurringPatternPublic(SQLModel):
    """Public recurring pattern model for API responses."""
    id: int
    user_id: uuid.UUID
    frequency: RecurrenceFrequency
    interval: int
    start_date: datetime
    weekly_days: Optional[List[int]]
    monthly_day: Optional[int]
    end_type: RecurrenceEndType
    end_date: Optional[datetime]
    max_occurrences: Optional[int]
    current_occurrence: int
    created_at: datetime
    is_active: bool
