"""ActivityService for logging task operations."""

from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.activity_log import ActivityLog, ActivityAction, ActivityLogPublic


class ActivityService:
    """Service for activity logging and audit trail."""

    def __init__(self, session: Session):
        """Initialize activity service.

        Args:
            session: Database session
        """
        self.session = session

    async def log_activity(
        self,
        user_id: uuid.UUID,
        action: ActivityAction,
        entity_type: str = "task",
        entity_id: Optional[int] = None,
        task_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Log an activity.

        Args:
            user_id: User ID
            action: Action performed
            entity_type: Type of entity (task, user, etc.)
            entity_id: ID of the entity
            task_id: Task ID (if applicable)
            changes: Dictionary of changes made
            metadata: Additional metadata
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Created activity log entry
        """
        activity = ActivityLog(
            user_id=user_id,
            task_id=task_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)

        return activity

    async def get_user_activities(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        action: Optional[ActivityAction] = None,
        entity_type: Optional[str] = None
    ) -> List[ActivityLog]:
        """Get activities for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination
            action: Filter by action type
            entity_type: Filter by entity type

        Returns:
            List of activity logs
        """
        statement = select(ActivityLog).where(ActivityLog.user_id == user_id)

        if action:
            statement = statement.where(ActivityLog.action == action)

        if entity_type:
            statement = statement.where(ActivityLog.entity_type == entity_type)

        statement = statement.order_by(ActivityLog.created_at.desc())
        statement = statement.limit(limit).offset(offset)

        result = self.session.exec(statement)
        return list(result.all())

    async def get_task_activities(
        self,
        task_id: int,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activities for a specific task.

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of activity logs for the task
        """
        statement = select(ActivityLog).where(
            ActivityLog.task_id == task_id,
            ActivityLog.user_id == user_id
        )

        statement = statement.order_by(ActivityLog.created_at.desc())
        statement = statement.limit(limit).offset(offset)

        result = self.session.exec(statement)
        return list(result.all())

    async def get_recent_activities(
        self,
        user_id: uuid.UUID,
        hours: int = 24,
        limit: int = 100
    ) -> List[ActivityLog]:
        """Get recent activities within a time window.

        Args:
            user_id: User ID
            hours: Number of hours to look back
            limit: Maximum number of results

        Returns:
            List of recent activity logs
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        statement = select(ActivityLog).where(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= cutoff_time
        )

        statement = statement.order_by(ActivityLog.created_at.desc())
        statement = statement.limit(limit)

        result = self.session.exec(statement)
        return list(result.all())

    async def delete_old_activities(
        self,
        days: int = 90
    ) -> int:
        """Delete activity logs older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of deleted records
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        statement = select(ActivityLog).where(
            ActivityLog.created_at < cutoff_time
        )

        result = self.session.exec(statement)
        activities = result.all()

        for activity in activities:
            self.session.delete(activity)

        await self.session.commit()

        return len(activities)
