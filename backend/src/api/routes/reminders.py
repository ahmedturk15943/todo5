"""Reminder API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import List
import uuid

from ...database import get_session
from ...models import Reminder, ReminderCreate, ReminderPublic, ReminderStatus
from ...services.reminder_service import ReminderService
from ...services.notification_service import NotificationService
from ...api.dependencies import get_current_user
from ...dapr import DaprJobsClient

router = APIRouter()


@router.post("/reminders", response_model=ReminderPublic, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new reminder for a task.

    Args:
        reminder_data: Reminder creation data
        current_user: Authenticated user
        session: Database session

    Returns:
        Created reminder
    """
    jobs_client = DaprJobsClient()
    service = ReminderService(session, jobs_client)
    user_id = uuid.UUID(current_user["id"])

    reminder = await service.create_reminder(
        user_id=user_id,
        task_id=reminder_data.task_id,
        remind_at=reminder_data.remind_at
    )

    return reminder


@router.get("/reminders", response_model=List[ReminderPublic])
async def list_reminders(
    task_id: int = None,
    status: ReminderStatus = None,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List user's reminders.

    Args:
        task_id: Filter by task ID
        status: Filter by status
        current_user: Authenticated user
        session: Database session

    Returns:
        List of reminders
    """
    jobs_client = DaprJobsClient()
    service = ReminderService(session, jobs_client)
    user_id = uuid.UUID(current_user["id"])

    reminders = await service.list_reminders(user_id, task_id, status)

    return reminders


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reminder(
    reminder_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Cancel a scheduled reminder.

    Args:
        reminder_id: Reminder ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: If reminder not found
    """
    jobs_client = DaprJobsClient()
    service = ReminderService(session, jobs_client)
    user_id = uuid.UUID(current_user["id"])

    success = await service.cancel_reminder(reminder_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found or already processed"
        )

    return None


@router.post("/jobs/trigger")
async def handle_job_trigger(request: Request, session: Session = Depends(get_session)):
    """Handle Dapr Jobs API callback when reminder fires.

    Args:
        request: FastAPI request
        session: Database session

    Returns:
        Job execution status
    """
    job_data = await request.json()

    reminder_id = job_data.get("data", {}).get("reminder_id")
    task_id = job_data.get("data", {}).get("task_id")

    if not reminder_id or not task_id:
        return {"status": "FAILURE", "message": "Missing reminder_id or task_id"}

    # Get reminder and task
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        return {"status": "FAILURE", "message": "Reminder not found"}

    from ...models import Task
    task = session.get(Task, task_id)
    if not task:
        return {"status": "FAILURE", "message": "Task not found"}

    # Send notification
    notification_service = NotificationService()
    success = await notification_service.send_reminder(reminder, task)

    # Update reminder status
    jobs_client = DaprJobsClient()
    reminder_service = ReminderService(session, jobs_client)
    await reminder_service.mark_sent(
        reminder_id,
        success=success,
        error_message=None if success else "Notification delivery failed"
    )

    return {"status": "SUCCESS" if success else "FAILURE"}
