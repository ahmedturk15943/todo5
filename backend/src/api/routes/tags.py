"""Tag API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import uuid

from ...database import get_session
from ...models import Tag, TagCreate, TagPublic, TagUpdate
from ...api.dependencies import get_current_user

router = APIRouter()


@router.post("/tags", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tag.

    Args:
        tag_data: Tag creation data
        current_user: Authenticated user
        session: Database session

    Returns:
        Created tag
    """
    user_id = uuid.UUID(current_user["id"])

    # Check for duplicate tag name
    statement = select(Tag).where(
        Tag.user_id == user_id,
        Tag.name == tag_data.name
    )
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )

    tag = Tag(
        user_id=user_id,
        **tag_data.model_dump()
    )

    session.add(tag)
    session.commit()
    session.refresh(tag)

    return tag


@router.get("/tags", response_model=List[TagPublic])
async def list_tags(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List user's tags.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        List of tags
    """
    user_id = uuid.UUID(current_user["id"])

    statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
    result = session.exec(statement)

    return list(result.all())


@router.get("/tags/{tag_id}", response_model=TagPublic)
async def get_tag(
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get tag by ID.

    Args:
        tag_id: Tag ID
        current_user: Authenticated user
        session: Database session

    Returns:
        Tag

    Raises:
        HTTPException: If tag not found
    """
    user_id = uuid.UUID(current_user["id"])

    statement = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == user_id
    )
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


@router.put("/tags/{tag_id}", response_model=TagPublic)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a tag.

    Args:
        tag_id: Tag ID
        tag_data: Tag update data
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated tag

    Raises:
        HTTPException: If tag not found
    """
    user_id = uuid.UUID(current_user["id"])

    statement = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == user_id
    )
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Update fields
    update_dict = tag_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(tag, key, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)

    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a tag.

    Args:
        tag_id: Tag ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: If tag not found
    """
    user_id = uuid.UUID(current_user["id"])

    statement = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == user_id
    )
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    session.delete(tag)
    session.commit()

    return None


@router.post("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_task(
    task_id: int,
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add tag to task.

    Args:
        task_id: Task ID
        tag_id: Tag ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: If task or tag not found
    """
    from ...services.task_service import TaskService

    user_id = uuid.UUID(current_user["id"])
    service = TaskService(session)

    # Verify task exists and belongs to user
    task = await service.get_task(task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify tag exists and belongs to user
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Add tag to task
    await service.add_tags_to_task(task_id, [tag_id])

    return None


@router.delete("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_task(
    task_id: int,
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove tag from task.

    Args:
        task_id: Task ID
        tag_id: Tag ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: If task or tag not found
    """
    from ...services.task_service import TaskService

    user_id = uuid.UUID(current_user["id"])
    service = TaskService(session)

    # Verify task exists and belongs to user
    task = await service.get_task(task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Remove tag from task
    success = await service.remove_tag_from_task(task_id, tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not associated with this task"
        )

    return None
