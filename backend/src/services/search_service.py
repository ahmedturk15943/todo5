"""SearchService for advanced search and filtering."""

from sqlmodel import Session, select, func, or_
from typing import Optional, List
from datetime import datetime
import uuid

from ..models import Task, TaskStatus, PriorityLevel, Tag, TaskTag


class SearchService:
    """Service for advanced task search and filtering."""

    def __init__(self, session: Session):
        """Initialize search service.

        Args:
            session: Database session
        """
        self.session = session

    async def search_tasks(
        self,
        user_id: uuid.UUID,
        query: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[PriorityLevel] = None,
        tags: Optional[List[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """Search and filter tasks with full-text search.

        Args:
            user_id: User ID
            query: Search query for full-text search
            status: Filter by status
            priority: Filter by priority
            tags: Filter by tag names
            due_date_start: Filter by due date start
            due_date_end: Filter by due date end
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            limit: Result limit
            offset: Result offset

        Returns:
            List of matching tasks
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Full-text search
        if query:
            # Use PostgreSQL full-text search
            statement = statement.where(
                func.to_tsvector('english', Task.title + ' ' + func.coalesce(Task.description, '')).match(query)
            )

        # Status filter
        if status:
            statement = statement.where(Task.status == status)

        # Priority filter
        if priority:
            statement = statement.where(Task.priority == priority)

        # Tag filter
        if tags:
            # Join with tags and filter
            statement = statement.join(TaskTag).join(Tag).where(Tag.name.in_(tags))

        # Due date range filter
        if due_date_start:
            statement = statement.where(Task.due_date >= due_date_start)

        if due_date_end:
            statement = statement.where(Task.due_date <= due_date_end)

        # Sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        # Pagination
        statement = statement.limit(limit).offset(offset)

        result = self.session.exec(statement)
        return list(result.all())

    async def get_task_count(
        self,
        user_id: uuid.UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[PriorityLevel] = None
    ) -> dict:
        """Get task counts by status and priority.

        Args:
            user_id: User ID
            status: Filter by status
            priority: Filter by priority

        Returns:
            Dictionary with counts
        """
        statement = select(func.count(Task.id)).where(Task.user_id == user_id)

        if status:
            statement = statement.where(Task.status == status)

        if priority:
            statement = statement.where(Task.priority == priority)

        total = self.session.exec(statement).one()

        return {
            "total": total,
            "status": status.value if status else "all",
            "priority": priority.value if priority else "all"
        }
