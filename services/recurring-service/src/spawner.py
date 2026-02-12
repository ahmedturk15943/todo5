"""Task spawner logic for recurring tasks."""

from datetime import datetime
from typing import Optional
from sqlmodel import Session

from backend.src.models import Task, RecurringPattern, TaskStatus
from backend.src.services.recurring_service import RecurringService


class TaskSpawner:
    """Spawns next occurrence of recurring tasks."""

    def __init__(self, session: Session):
        """Initialize task spawner.

        Args:
            session: Database session
        """
        self.session = session
        self.recurring_service = RecurringService(session)

    async def spawn_from_completed_task(
        self,
        completed_task: Task,
        pattern: RecurringPattern
    ) -> Optional[Task]:
        """Spawn next occurrence from completed task.

        Args:
            completed_task: The task that was just completed
            pattern: Recurring pattern

        Returns:
            New task instance or None if pattern ended
        """
        # Calculate next occurrence date
        next_date = self.recurring_service.calculate_next_occurrence(
            pattern,
            completed_task.completed_at
        )

        if not next_date:
            return None

        # Create new task with same attributes
        new_task = Task(
            user_id=completed_task.user_id,
            title=completed_task.title,
            description=completed_task.description,
            priority=completed_task.priority,
            due_date=next_date,
            recurring_pattern_id=pattern.id,
            parent_task_id=completed_task.id,
            status=TaskStatus.INCOMPLETE
        )

        self.session.add(new_task)

        # Increment occurrence counter
        pattern.current_occurrence += 1
        self.session.add(pattern)

        self.session.commit()
        self.session.refresh(new_task)

        return new_task
