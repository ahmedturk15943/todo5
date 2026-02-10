# Data Model: Advanced Cloud Deployment

**Feature**: Advanced Cloud Deployment with Enhanced Task Management
**Date**: 2026-02-10
**Status**: Complete

## Overview

This document defines the data model for Phase 5, extending the existing Phase 2 schema with new entities for recurring tasks, reminders, tags, priorities, and activity logging. All entities use SQLModel for Python and maintain compatibility with Neon PostgreSQL.

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│ (existing)  │
└──────┬──────┘
       │ 1
       │
       │ *
┌──────┴──────────────────────────────────────────────────────────────┐
│                            Task (extended)                           │
│ - id, title, description, status, user_id (existing)                │
│ - priority (NEW): enum(high, medium, low)                           │
│ - due_date (NEW): datetime                                          │
│ - recurring_pattern_id (NEW): FK → RecurringPattern                 │
│ - parent_task_id (NEW): FK → Task (for recurring instances)         │
│ - created_at, updated_at, completed_at                              │
│ - version (NEW): int (optimistic locking)                           │
│ - search_vector (NEW): tsvector (full-text search)                  │
└──────┬───────────────┬──────────────┬──────────────┬────────────────┘
       │ 1             │ 1            │ *            │ *
       │               │              │              │
       │ 0..1          │ *            │              │
┌──────┴──────┐ ┌──────┴──────┐ ┌────┴─────┐ ┌──────┴──────┐
│  Recurring  │ │   Reminder  │ │ TaskTag  │ │ ActivityLog │
│   Pattern   │ │             │ │ (join)   │ │             │
└─────────────┘ └─────────────┘ └────┬─────┘ └─────────────┘
                                     │ *
                                     │
                                     │ 1
                              ┌──────┴──────┐
                              │     Tag     │
                              └─────────────┘

┌─────────────────────┐
│ NotificationPref    │
│ (per user)          │
└─────────────────────┘
```

## Core Entities

### 1. Task (Extended)

**Purpose**: Represents a user's to-do item with enhanced attributes for priority, due dates, recurrence, and tags.

**Schema**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import TSVECTOR
from datetime import datetime
from enum import Enum
from typing import Optional, List

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
    """Task entity with enhanced attributes."""
    __tablename__ = "tasks"

    # Existing fields from Phase 2
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)

    # NEW: Priority and organization
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, index=True)

    # NEW: Due dates and reminders
    due_date: Optional[datetime] = Field(default=None, index=True)

    # NEW: Recurring task support
    recurring_pattern_id: Optional[int] = Field(
        default=None,
        foreign_key="recurring_patterns.id"
    )
    parent_task_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id"
    )  # Links to original recurring task

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # NEW: Optimistic locking for conflict detection
    version: int = Field(default=1)

    # NEW: Full-text search vector (auto-updated via trigger)
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR)
    )

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    recurring_pattern: Optional["RecurringPattern"] = Relationship(
        back_populates="tasks"
    )
    reminders: List["Reminder"] = Relationship(
        back_populates="task",
        cascade_delete=True
    )
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model="TaskTag"
    )
    activity_logs: List["ActivityLog"] = Relationship(
        back_populates="task",
        cascade_delete=True
    )
    child_tasks: List["Task"] = Relationship(
        back_populates="parent_task",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    parent_task: Optional["Task"] = Relationship(back_populates="child_tasks")
```

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN(search_vector);
```

**Validation Rules**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 2000 characters
- `due_date`: Must be in the future when creating (can be past for overdue tasks)
- `priority`: Must be one of: high, medium, low
- `recurring_pattern_id`: Must reference valid RecurringPattern if set
- `parent_task_id`: Must reference valid Task if set (for recurring instances)

**State Transitions**:
- `incomplete` → `complete`: Mark task as done, set `completed_at`
- `complete` → `incomplete`: Reopen task, clear `completed_at`
- When recurring task completed: Trigger event to spawn next occurrence

---

### 2. RecurringPattern (NEW)

**Purpose**: Defines how a task repeats (daily, weekly, monthly, custom intervals).

**Schema**:
```python
from enum import Enum

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
    user_id: str = Field(foreign_key="users.id", index=True)

    # Recurrence definition
    frequency: RecurrenceFrequency = Field(index=True)
    interval: int = Field(default=1, ge=1)  # Every N days/weeks/months
    start_date: datetime = Field(index=True)

    # Weekly: specific days (e.g., [1, 3, 5] for Mon, Wed, Fri)
    weekly_days: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))

    # Monthly: specific date (e.g., 15 for 15th of each month)
    monthly_day: Optional[int] = Field(default=None, ge=1, le=31)

    # End condition
    end_type: RecurrenceEndType = Field(default=RecurrenceEndType.NEVER)
    end_date: Optional[datetime] = Field(default=None)
    max_occurrences: Optional[int] = Field(default=None, ge=1)
    current_occurrence: int = Field(default=0)  # Track count

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="recurring_patterns")
    tasks: List["Task"] = Relationship(back_populates="recurring_pattern")
```

**Examples**:
```python
# Daily standup (every day)
RecurringPattern(
    frequency=RecurrenceFrequency.DAILY,
    interval=1,
    start_date=datetime(2026, 2, 10, 9, 0),
    end_type=RecurrenceEndType.NEVER
)

# Weekly team meeting (every Monday)
RecurringPattern(
    frequency=RecurrenceFrequency.WEEKLY,
    interval=1,
    weekly_days=[0],  # Monday (0=Mon, 6=Sun)
    start_date=datetime(2026, 2, 10, 14, 0),
    end_type=RecurrenceEndType.NEVER
)

# Monthly report (15th of each month, for 12 months)
RecurringPattern(
    frequency=RecurrenceFrequency.MONTHLY,
    interval=1,
    monthly_day=15,
    start_date=datetime(2026, 2, 15, 9, 0),
    end_type=RecurrenceEndType.AFTER_OCCURRENCES,
    max_occurrences=12
)

# Every 2 weeks (bi-weekly)
RecurringPattern(
    frequency=RecurrenceFrequency.WEEKLY,
    interval=2,
    weekly_days=[0],  # Every other Monday
    start_date=datetime(2026, 2, 10, 10, 0),
    end_type=RecurrenceEndType.BY_DATE,
    end_date=datetime(2026, 12, 31)
)
```

**Validation Rules**:
- `interval`: Must be >= 1
- `weekly_days`: Required if frequency is WEEKLY, values 0-6 (Mon-Sun)
- `monthly_day`: Required if frequency is MONTHLY, values 1-31
- `end_date`: Required if end_type is BY_DATE, must be after start_date
- `max_occurrences`: Required if end_type is AFTER_OCCURRENCES, must be >= 1

---

### 3. Reminder (NEW)

**Purpose**: Scheduled notifications for tasks with due dates.

**Schema**:
```python
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
    user_id: str = Field(foreign_key="users.id", index=True)

    # Scheduling
    remind_at: datetime = Field(index=True)  # When to send reminder
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Delivery tracking
    status: ReminderStatus = Field(default=ReminderStatus.PENDING, index=True)
    sent_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Dapr Jobs API integration
    job_id: Optional[str] = Field(default=None, unique=True)  # Dapr job ID

    # Relationships
    task: "Task" = Relationship(back_populates="reminders")
    user: "User" = Relationship(back_populates="reminders")
```

**Indexes**:
```sql
CREATE INDEX idx_reminders_task_id ON reminders(task_id);
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX idx_reminders_status ON reminders(status);
CREATE INDEX idx_reminders_pending ON reminders(status, remind_at) WHERE status = 'pending';
```

**Validation Rules**:
- `remind_at`: Must be in the future when creating
- `task_id`: Must reference valid Task
- `user_id`: Must match task's user_id

**State Transitions**:
- `pending` → `sent`: Notification delivered successfully
- `pending` → `failed`: Notification delivery failed
- `pending` → `cancelled`: Task completed before reminder fired

---

### 4. Tag (NEW)

**Purpose**: Categorization labels for tasks (e.g., "work", "personal", "urgent").

**Schema**:
```python
class Tag(SQLModel, table=True):
    """Task categorization tag."""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color #RRGGBB
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tags")
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model="TaskTag"
    )

    # Unique constraint: user can't have duplicate tag names
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
    )
```

**Validation Rules**:
- `name`: Required, 1-50 characters, unique per user
- `color`: Optional, must be valid hex color (#RRGGBB)

---

### 5. TaskTag (NEW)

**Purpose**: Many-to-many relationship between Tasks and Tags.

**Schema**:
```python
class TaskTag(SQLModel, table=True):
    """Join table for Task-Tag many-to-many relationship."""
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
```sql
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

---

### 6. ActivityLog (NEW)

**Purpose**: Audit trail of all task operations for accountability and troubleshooting.

**Schema**:
```python
class ActivityType(str, Enum):
    """Types of task operations."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    REOPENED = "reopened"
    DELETED = "deleted"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    REMINDER_SET = "reminder_set"
    REMINDER_CANCELLED = "reminder_cancelled"

class ActivityLog(SQLModel, table=True):
    """Audit log of task operations."""
    __tablename__ = "activity_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)

    # Operation details
    activity_type: ActivityType = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Change details (JSON)
    changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"field": "title", "old": "Old Title", "new": "New Title"}

    # Metadata
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

    # Relationships
    task: "Task" = Relationship(back_populates="activity_logs")
    user: "User" = Relationship(back_populates="activity_logs")
```

**Indexes**:
```sql
CREATE INDEX idx_activity_logs_task_id ON activity_logs(task_id);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX idx_activity_logs_type ON activity_logs(activity_type);
CREATE INDEX idx_activity_logs_user_time ON activity_logs(user_id, timestamp);
```

**Retention Policy**:
- Logs retained for 90 days by default
- Automatic cleanup via scheduled job (Dapr Jobs API)
- Can be extended for enterprise users

---

### 7. NotificationPreference (NEW)

**Purpose**: User preferences for notification delivery channels and timing.

**Schema**:
```python
class NotificationPreference(SQLModel, table=True):
    """User notification preferences."""
    __tablename__ = "notification_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)

    # Channel preferences
    web_push_enabled: bool = Field(default=True)
    email_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)

    # Timing preferences
    quiet_hours_start: Optional[int] = Field(default=None, ge=0, le=23)  # Hour (0-23)
    quiet_hours_end: Optional[int] = Field(default=None, ge=0, le=23)
    timezone: str = Field(default="UTC", max_length=50)

    # Default reminder timing
    default_reminder_minutes: int = Field(default=60, ge=0)  # 1 hour before

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="notification_preference")
```

**Validation Rules**:
- `quiet_hours_start` and `quiet_hours_end`: Both required or both null
- `timezone`: Must be valid IANA timezone (e.g., "America/New_York")
- `default_reminder_minutes`: Must be >= 0

---

## Database Migrations

### Migration Strategy

**Approach**: Incremental migrations using Alembic (SQLModel/SQLAlchemy migration tool)

**Migration Steps**:

1. **Migration 001**: Add new columns to existing `tasks` table
   - Add `priority`, `due_date`, `recurring_pattern_id`, `parent_task_id`, `version`, `search_vector`
   - Create indexes
   - Set default values for existing tasks

2. **Migration 002**: Create new tables
   - `recurring_patterns`
   - `reminders`
   - `tags`
   - `task_tags`
   - `activity_logs`
   - `notification_preferences`

3. **Migration 003**: Create full-text search trigger
   - Create `tsvector_update_trigger` for auto-updating `search_vector`

4. **Migration 004**: Backfill data
   - Create default `NotificationPreference` for existing users
   - Initialize `version` to 1 for existing tasks

### Rollback Strategy

- Each migration has a `downgrade()` function
- Rollback removes new columns/tables in reverse order
- Data loss acceptable for new features (no existing data)
- Existing Phase 2 data preserved

---

## Data Integrity Constraints

### Foreign Key Constraints

```sql
-- Task references
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_recurring_pattern
    FOREIGN KEY (recurring_pattern_id) REFERENCES recurring_patterns(id) ON DELETE SET NULL;

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL;

-- Reminder references
ALTER TABLE reminders ADD CONSTRAINT fk_reminders_task
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

ALTER TABLE reminders ADD CONSTRAINT fk_reminders_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Tag references
ALTER TABLE tags ADD CONSTRAINT fk_tags_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- TaskTag references
ALTER TABLE task_tags ADD CONSTRAINT fk_task_tags_task
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

ALTER TABLE task_tags ADD CONSTRAINT fk_task_tags_tag
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE;

-- ActivityLog references
ALTER TABLE activity_logs ADD CONSTRAINT fk_activity_logs_task
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

ALTER TABLE activity_logs ADD CONSTRAINT fk_activity_logs_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- NotificationPreference references
ALTER TABLE notification_preferences ADD CONSTRAINT fk_notification_preferences_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

### Check Constraints

```sql
-- Task constraints
ALTER TABLE tasks ADD CONSTRAINT chk_tasks_priority
    CHECK (priority IN ('high', 'medium', 'low'));

ALTER TABLE tasks ADD CONSTRAINT chk_tasks_status
    CHECK (status IN ('incomplete', 'complete'));

ALTER TABLE tasks ADD CONSTRAINT chk_tasks_version
    CHECK (version >= 1);

-- RecurringPattern constraints
ALTER TABLE recurring_patterns ADD CONSTRAINT chk_recurring_interval
    CHECK (interval >= 1);

ALTER TABLE recurring_patterns ADD CONSTRAINT chk_recurring_monthly_day
    CHECK (monthly_day IS NULL OR (monthly_day >= 1 AND monthly_day <= 31));

ALTER TABLE recurring_patterns ADD CONSTRAINT chk_recurring_max_occurrences
    CHECK (max_occurrences IS NULL OR max_occurrences >= 1);

-- NotificationPreference constraints
ALTER TABLE notification_preferences ADD CONSTRAINT chk_notification_quiet_hours
    CHECK (
        (quiet_hours_start IS NULL AND quiet_hours_end IS NULL) OR
        (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)
    );

ALTER TABLE notification_preferences ADD CONSTRAINT chk_notification_default_reminder
    CHECK (default_reminder_minutes >= 0);
```

---

## Query Patterns

### Common Queries

**1. Get user's tasks with filters**:
```sql
SELECT t.*, array_agg(tag.name) as tags
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tag ON tt.tag_id = tag.id
WHERE t.user_id = :user_id
  AND t.status = :status  -- Optional filter
  AND t.priority = :priority  -- Optional filter
  AND t.due_date BETWEEN :start_date AND :end_date  -- Optional filter
  AND tag.name = ANY(:tag_names)  -- Optional filter
GROUP BY t.id
ORDER BY t.priority DESC, t.due_date ASC;
```

**2. Full-text search with filters**:
```sql
SELECT t.*, ts_rank(t.search_vector, query) as rank
FROM tasks t, to_tsquery('english', :search_query) query
WHERE t.user_id = :user_id
  AND t.search_vector @@ query
  AND t.priority = :priority  -- Optional filter
ORDER BY rank DESC, t.created_at DESC
LIMIT 50;
```

**3. Get pending reminders**:
```sql
SELECT r.*, t.title, t.due_date
FROM reminders r
JOIN tasks t ON r.task_id = t.id
WHERE r.status = 'pending'
  AND r.remind_at <= NOW() + INTERVAL '5 minutes'
ORDER BY r.remind_at ASC;
```

**4. Get recurring tasks due for spawning**:
```sql
SELECT t.*, rp.*
FROM tasks t
JOIN recurring_patterns rp ON t.recurring_pattern_id = rp.id
WHERE t.status = 'complete'
  AND t.completed_at IS NOT NULL
  AND rp.is_active = true
  AND (
    rp.end_type = 'never' OR
    (rp.end_type = 'after_occurrences' AND rp.current_occurrence < rp.max_occurrences) OR
    (rp.end_type = 'by_date' AND rp.end_date > NOW())
  );
```

**5. Get activity history for task**:
```sql
SELECT al.*, u.email as user_email
FROM activity_logs al
JOIN users u ON al.user_id = u.id
WHERE al.task_id = :task_id
ORDER BY al.timestamp DESC
LIMIT 100;
```

---

## Performance Considerations

### Indexing Strategy

- **Composite indexes** for common filter combinations (user_id + priority, user_id + due_date)
- **GIN index** on search_vector for fast full-text search
- **Partial indexes** for pending reminders (WHERE status = 'pending')
- **Covering indexes** for frequently accessed columns

### Query Optimization

- Use `EXPLAIN ANALYZE` to identify slow queries
- Implement query result caching (Redis) for common searches
- Paginate large result sets (LIMIT/OFFSET or cursor-based)
- Use database connection pooling (SQLAlchemy pool)

### Data Archival

- Archive completed tasks older than 1 year to separate table
- Archive activity logs older than 90 days
- Implement soft deletes for tasks (add `deleted_at` column)

---

## Summary

This data model extends Phase 2's schema with 7 new entities and enhanced Task entity, supporting:
- Recurring tasks with flexible patterns
- Scheduled reminders with delivery tracking
- Priority levels and tag-based organization
- Full-text search with relevance ranking
- Complete activity audit trail
- User notification preferences

All entities maintain clean relationships, proper indexing, and data integrity constraints for production use.
