"""Activity API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
import uuid

from ...database import get_session
from ...models.activity_log import ActivityLog, ActivityLogPublic, ActivityAction
from ...services.activity_service import ActivityService
from ...api.dependencies import get_current_user

router = APIRouter()


@router.get("/activity", response_model=List[ActivityLogPublic])
async def get_user_activities(
    limit: int = Query(50, ge=1, le=100, description="Result limit"),
    offset: int = Query(0, ge=0, description="Result offset"),
    action: Optional[ActivityAction] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get activity logs for the current user.

    Args:
        limit: Maximum number of results
        offset: Offset for pagination
        action: Filter by action type
        entity_type: Filter by entity type
        current_user: Authenticated user
        session: Database session

    Returns:
        List of activity logs
    """
    service = ActivityService(session)
    user_id = uuid.UUID(current_user["id"])

    activities = await service.get_user_activities(
        user_id=user_id,
        limit=limit,
        offset=offset,
        action=action,
        entity_type=entity_type
    )

    return activities


@router.get("/activity/task/{task_id}", response_model=List[ActivityLogPublic])
async def get_task_activities(
    task_id: int,
    limit: int = Query(50, ge=1, le=100, description="Result limit"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get activity logs for a specific task.

    Args:
        task_id: Task ID
        limit: Maximum number of results
        offset: Offset for pagination
        current_user: Authenticated user
        session: Database session

    Returns:
        List of activity logs for the task
    """
    service = ActivityService(session)
    user_id = uuid.UUID(current_user["id"])

    activities = await service.get_task_activities(
        task_id=task_id,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return activities


@router.get("/activity/recent", response_model=List[ActivityLogPublic])
async def get_recent_activities(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=500, description="Result limit"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get recent activities within a time window.

    Args:
        hours: Number of hours to look back
        limit: Maximum number of results
        current_user: Authenticated user
        session: Database session

    Returns:
        List of recent activity logs
    """
    service = ActivityService(session)
    user_id = uuid.UUID(current_user["id"])

    activities = await service.get_recent_activities(
        user_id=user_id,
        hours=hours,
        limit=limit
    )

    return activities
