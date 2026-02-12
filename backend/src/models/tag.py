"""Tag model for task categorization."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class Tag(SQLModel, table=True):
    """Task categorization tag."""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color #RRGGBB
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model="TaskTag")


class TaskTag(SQLModel, table=True):
    """Join table for Task-Tag many-to-many relationship."""
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TagCreate(SQLModel):
    """Model for creating a tag."""
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagPublic(SQLModel):
    """Public tag model for API responses."""
    id: int
    user_id: uuid.UUID
    name: str
    color: Optional[str]
    created_at: datetime


class TagUpdate(SQLModel):
    """Model for updating a tag."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)
