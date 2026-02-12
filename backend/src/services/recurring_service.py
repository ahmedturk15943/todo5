"""RecurringService for managing recurring task patterns and spawning."""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlmodel import Session, select
from dateutil.relativedelta import relativedelta
import uuid

from ..models import (
    RecurringPattern,
    RecurringPatternCreate,
    RecurrenceFrequency,
    RecurrenceEndType,
    Task,
    TaskCreate,
    TaskStatus,
)


class RecurringService:
    """Service for recurring task pattern management."""

    def __init__(self, session: Session):
        """Initialize recurring service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_pattern(
        self,
        user_id: uuid.UUID,
        pattern_data: RecurringPatternCreate
    ) -> RecurringPattern:
        """Create a new recurring pattern.

        Args:
            user_id: User ID
            pattern_data: Pattern creation data

        Returns:
            Created recurring pattern
        """
        pattern = RecurringPattern(
            user_id=user_id,
            **pattern_data.model_dump()
        )

        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    async def get_pattern(
        self,
        pattern_id: int,
        user_id: uuid.UUID
    ) -> Optional[RecurringPattern]:
        """Get recurring pattern by ID.

        Args:
            pattern_id: Pattern ID
            user_id: User ID (for authorization)

        Returns:
            Recurring pattern or None
        """
        statement = select(RecurringPattern).where(
            RecurringPattern.id == pattern_id,
            RecurringPattern.user_id == user_id
        )
        result = self.session.exec(statement)
        return result.first()

    async def list_patterns(
        self,
        user_id: uuid.UUID,
        active_only: bool = True
    ) -> List[RecurringPattern]:
        """List user's recurring patterns.

        Args:
            user_id: User ID
            active_only: Only return active patterns

        Returns:
            List of recurring patterns
        """
        statement = select(RecurringPattern).where(
            RecurringPattern.user_id == user_id
        )

        if active_only:
            statement = statement.where(RecurringPattern.is_active == True)

        result = self.session.exec(statement)
        return list(result.all())

    async def deactivate_pattern(
        self,
        pattern_id: int,
        user_id: uuid.UUID
    ) -> bool:
        """Deactivate a recurring pattern.

        Args:
            pattern_id: Pattern ID
            user_id: User ID

        Returns:
            True if deactivated
        """
        pattern = await self.get_pattern(pattern_id, user_id)

        if not pattern:
            return False

        pattern.is_active = False
        self.session.add(pattern)
        self.session.commit()

        return True

    def calculate_next_occurrence(
        self,
        pattern: RecurringPattern,
        from_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Calculate next occurrence date based on pattern.

        Args:
            pattern: Recurring pattern
            from_date: Calculate from this date (default: now)

        Returns:
            Next occurrence datetime or None if pattern ended
        """
        if not pattern.is_active:
            return None

        # Check if pattern has ended
        if pattern.end_type == RecurrenceEndType.AFTER_OCCURRENCES:
            if pattern.current_occurrence >= pattern.max_occurrences:
                return None

        if pattern.end_type == RecurrenceEndType.BY_DATE:
            if pattern.end_date and datetime.utcnow() >= pattern.end_date:
                return None

        base_date = from_date or datetime.utcnow()

        # Calculate next occurrence based on frequency
        if pattern.frequency == RecurrenceFrequency.DAILY:
            next_date = base_date + timedelta(days=pattern.interval)

        elif pattern.frequency == RecurrenceFrequency.WEEKLY:
            # Find next occurrence on specified weekdays
            next_date = base_date + timedelta(days=1)
            days_checked = 0

            while days_checked < 7 * pattern.interval:
                if next_date.weekday() in (pattern.weekly_days or []):
                    break
                next_date += timedelta(days=1)
                days_checked += 1

        elif pattern.frequency == RecurrenceFrequency.MONTHLY:
            # Next occurrence on specified day of month
            next_date = base_date + relativedelta(months=pattern.interval)

            if pattern.monthly_day:
                # Handle months with fewer days
                try:
                    next_date = next_date.replace(day=pattern.monthly_day)
                except ValueError:
                    # If day doesn't exist in month, use last day
                    next_date = next_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)

        else:
            # Custom frequency
            next_date = base_date + timedelta(days=pattern.interval)

        return next_date

    async def spawn_next_occurrence(
        self,
        task: Task,
        pattern: RecurringPattern
    ) -> Optional[Task]:
        """Spawn next occurrence of a recurring task.

        Args:
            task: Completed task
            pattern: Recurring pattern

        Returns:
            New task instance or None if pattern ended
        """
        next_date = self.calculate_next_occurrence(pattern, task.completed_at)

        if not next_date:
            return None

        # Create new task instance
        new_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=next_date,
            recurring_pattern_id=pattern.id,
            parent_task_id=task.id,
            status=TaskStatus.INCOMPLETE
        )

        self.session.add(new_task)

        # Increment occurrence counter
        pattern.current_occurrence += 1
        self.session.add(pattern)

        self.session.commit()
        self.session.refresh(new_task)

        return new_task
