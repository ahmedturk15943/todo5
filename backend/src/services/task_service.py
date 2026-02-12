"""Task service for CRUD operations."""

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
import html
from datetime import datetime

from ..models.task import Task, TaskCreate, TaskUpdate


class OptimisticLockError(Exception):
    """Raised when optimistic locking detects a conflict."""
    pass


class TaskService:
    """Service for task operations."""

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML to prevent XSS attacks."""
        return html.escape(text)

    @staticmethod
    async def get_all_tasks(user_id: uuid.UUID, session: AsyncSession) -> List[Task]:
        """
        Get all tasks for a user.

        Args:
            user_id: User's UUID
            session: Database session

        Returns:
            List of tasks ordered by creation date (newest first)
        """
        result = await session.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        tasks = result.scalars().all()
        return list(tasks)

    @staticmethod
    async def get_task_by_id(
        task_id: int, user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[Task]:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID
            user_id: User's UUID (for authorization)
            session: Database session

        Returns:
            Task if found and belongs to user, None otherwise
        """
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_task(
        user_id: uuid.UUID, task_data: TaskCreate, session: AsyncSession
    ) -> Task:
        """
        Create a new task.

        Args:
            user_id: User's UUID
            task_data: Task creation data
            session: Database session

        Returns:
            Created task

        Raises:
            ValueError: If validation fails
        """
        # Validate and escape title
        title = task_data.title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        title = TaskService._escape_html(title)

        # Validate and escape description
        description = None
        if task_data.description:
            description = task_data.description.strip()
            if description:
                description = TaskService._escape_html(description)

        # Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def update_task(
        task_id: int,
        user_id: uuid.UUID,
        task_data: TaskUpdate,
        session: AsyncSession,
        expected_version: Optional[int] = None,
    ) -> Optional[Task]:
        """
        Update a task with optimistic locking.

        Args:
            task_id: Task ID
            user_id: User's UUID (for authorization)
            task_data: Task update data
            session: Database session
            expected_version: Expected version for optimistic locking

        Returns:
            Updated task if found, None otherwise

        Raises:
            ValueError: If validation fails
            OptimisticLockError: If version mismatch detected
        """
        # Get existing task
        task = await TaskService.get_task_by_id(task_id, user_id, session)
        if not task:
            return None

        # Optimistic locking check
        if expected_version is not None:
            current_version = getattr(task, 'version', 1)
            if current_version != expected_version:
                raise OptimisticLockError(
                    f"Task has been modified by another process. "
                    f"Expected version {expected_version}, but current version is {current_version}"
                )

        # Update title if provided
        if task_data.title is not None:
            title = task_data.title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            task.title = TaskService._escape_html(title)

        # Update description if provided
        if task_data.description is not None:
            description = task_data.description.strip()
            task.description = TaskService._escape_html(description) if description else None

        # Update timestamp and increment version
        task.updated_at = datetime.utcnow()
        if hasattr(task, 'version'):
            task.version = (task.version or 1) + 1

        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def delete_task(
        task_id: int, user_id: uuid.UUID, session: AsyncSession
    ) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: User's UUID (for authorization)
            session: Database session

        Returns:
            True if deleted, False if not found
        """
        task = await TaskService.get_task_by_id(task_id, user_id, session)
        if not task:
            return False

        await session.delete(task)
        await session.commit()

        return True

    @staticmethod
    async def toggle_complete(
        task_id: int, user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[Task]:
        """
        Toggle task completion status.

        Args:
            task_id: Task ID
            user_id: User's UUID (for authorization)
            session: Database session

        Returns:
            Updated task if found, None otherwise
        """
        task = await TaskService.get_task_by_id(task_id, user_id, session)
        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        return task


# Import datetime for updated_at
from datetime import datetime
