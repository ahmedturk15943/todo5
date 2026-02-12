"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ...database import get_session
from ...models import Task, TaskPublic, TaskStatus, PriorityLevel
from ...services.search_service import SearchService
from ...api.dependencies import get_current_user

router = APIRouter()


@router.get("/search", response_model=List[TaskPublic])
async def search_tasks(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names"),
    due_date_start: Optional[datetime] = Query(None, description="Due date start"),
    due_date_end: Optional[datetime] = Query(None, description="Due date end"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(50, ge=1, le=100, description="Result limit"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Search and filter tasks.

    Args:
        q: Search query for full-text search
        status: Filter by status
        priority: Filter by priority
        tags: Comma-separated tag names
        due_date_start: Filter by due date start
        due_date_end: Filter by due date end
        sort_by: Sort field
        sort_order: Sort order
        limit: Result limit
        offset: Result offset
        current_user: Authenticated user
        session: Database session

    Returns:
        List of matching tasks
    """
    service = SearchService(session)
    user_id = uuid.UUID(current_user["id"])

    # Parse tags
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]

    tasks = await service.search_tasks(
        user_id=user_id,
        query=q,
        status=status,
        priority=priority,
        tags=tag_list,
        due_date_start=due_date_start,
        due_date_end=due_date_end,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    return tasks


@router.get("/search/count")
async def get_task_counts(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[PriorityLevel] = Query(None),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get task counts by status and priority.

    Args:
        status: Filter by status
        priority: Filter by priority
        current_user: Authenticated user
        session: Database session

    Returns:
        Task counts
    """
    service = SearchService(session)
    user_id = uuid.UUID(current_user["id"])

    counts = await service.get_task_count(user_id, status, priority)

    return counts
