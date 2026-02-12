"""Recurring task API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import uuid

from ...database import get_session
from ...models import (
    RecurringPattern,
    RecurringPatternCreate,
    RecurringPatternPublic,
)
from ...services.recurring_service import RecurringService
from ...api.dependencies import get_current_user

router = APIRouter()


@router.post("/recurring", response_model=RecurringPatternPublic, status_code=status.HTTP_201_CREATED)
async def create_recurring_pattern(
    pattern_data: RecurringPatternCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new recurring pattern.

    Args:
        pattern_data: Recurring pattern creation data
        current_user: Authenticated user
        session: Database session

    Returns:
        Created recurring pattern
    """
    service = RecurringService(session)
    user_id = uuid.UUID(current_user["id"])

    pattern = await service.create_pattern(user_id, pattern_data)

    return pattern


@router.get("/recurring", response_model=List[RecurringPatternPublic])
async def list_recurring_patterns(
    active_only: bool = True,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List user's recurring patterns.

    Args:
        active_only: Only return active patterns
        current_user: Authenticated user
        session: Database session

    Returns:
        List of recurring patterns
    """
    service = RecurringService(session)
    user_id = uuid.UUID(current_user["id"])

    patterns = await service.list_patterns(user_id, active_only)

    return patterns


@router.get("/recurring/{pattern_id}", response_model=RecurringPatternPublic)
async def get_recurring_pattern(
    pattern_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get recurring pattern by ID.

    Args:
        pattern_id: Pattern ID
        current_user: Authenticated user
        session: Database session

    Returns:
        Recurring pattern

    Raises:
        HTTPException: If pattern not found
    """
    service = RecurringService(session)
    user_id = uuid.UUID(current_user["id"])

    pattern = await service.get_pattern(pattern_id, user_id)

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring pattern not found"
        )

    return pattern


@router.delete("/recurring/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_recurring_pattern(
    pattern_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Deactivate a recurring pattern.

    Args:
        pattern_id: Pattern ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: If pattern not found
    """
    service = RecurringService(session)
    user_id = uuid.UUID(current_user["id"])

    success = await service.deactivate_pattern(pattern_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring pattern not found"
        )

    return None
