"""ReminderService for scheduling and managing task reminders."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
import uuid

from ..models import Reminder, ReminderCreate, ReminderStatus
from ..dapr import DaprJobsClient


class ReminderService:
    """Service for reminder scheduling and management."""

    def __init__(self, session: Session, jobs_client: DaprJobsClient):
        """Initialize reminder service.

        Args:
            session: Database session
            jobs_client: Dapr Jobs API client
        """
        self.session = session
        self.jobs_client = jobs_client

    async def create_reminder(
        self,
        user_id: uuid.UUID,
        task_id: int,
        remind_at: datetime
    ) -> Reminder:
        """Create and schedule a new reminder.

        Args:
            user_id: User ID
            task_id: Task ID
            remind_at: When to send reminder

        Returns:
            Created reminder
        """
        # Create reminder record
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            remind_at=remind_at,
            status=ReminderStatus.PENDING
        )

        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        # Schedule via Dapr Jobs API
        job_name = f"reminder-task-{task_id}-{reminder.id}"
        success = await self.jobs_client.schedule_reminder(
            task_id=task_id,
            user_id=str(user_id),
            remind_at=remind_at,
            reminder_id=reminder.id
        )

        if success:
            reminder.job_id = job_name
            self.session.add(reminder)
            self.session.commit()

        return reminder

    async def get_reminder(
        self,
        reminder_id: int,
        user_id: uuid.UUID
    ) -> Optional[Reminder]:
        """Get reminder by ID.

        Args:
            reminder_id: Reminder ID
            user_id: User ID (for authorization)

        Returns:
            Reminder or None
        """
        statement = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        result = self.session.exec(statement)
        return result.first()

    async def list_reminders(
        self,
        user_id: uuid.UUID,
        task_id: Optional[int] = None,
        status: Optional[ReminderStatus] = None
    ) -> List[Reminder]:
        """List user's reminders.

        Args:
            user_id: User ID
            task_id: Filter by task ID
            status: Filter by status

        Returns:
            List of reminders
        """
        statement = select(Reminder).where(Reminder.user_id == user_id)

        if task_id:
            statement = statement.where(Reminder.task_id == task_id)

        if status:
            statement = statement.where(Reminder.status == status)

        statement = statement.order_by(Reminder.remind_at)

        result = self.session.exec(statement)
        return list(result.all())

    async def cancel_reminder(
        self,
        reminder_id: int,
        user_id: uuid.UUID
    ) -> bool:
        """Cancel a scheduled reminder.

        Args:
            reminder_id: Reminder ID
            user_id: User ID

        Returns:
            True if cancelled
        """
        reminder = await self.get_reminder(reminder_id, user_id)

        if not reminder or reminder.status != ReminderStatus.PENDING:
            return False

        # Cancel Dapr job
        if reminder.job_id:
            await self.jobs_client.cancel_job(reminder.job_id)

        # Update status
        reminder.status = ReminderStatus.CANCELLED
        self.session.add(reminder)
        self.session.commit()

        return True

    async def mark_sent(
        self,
        reminder_id: int,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """Mark reminder as sent or failed.

        Args:
            reminder_id: Reminder ID
            success: Whether notification was sent successfully
            error_message: Error message if failed

        Returns:
            True if updated
        """
        reminder = self.session.get(Reminder, reminder_id)

        if not reminder:
            return False

        if success:
            reminder.status = ReminderStatus.SENT
            reminder.sent_at = datetime.utcnow()
        else:
            reminder.status = ReminderStatus.FAILED
            reminder.error_message = error_message

        self.session.add(reminder)
        self.session.commit()

        return True
