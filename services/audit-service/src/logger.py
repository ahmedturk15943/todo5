"""Activity logger for database operations."""

import os
import logging
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from datetime import datetime

logger = logging.getLogger(__name__)


class ActivityLogger:
    """Logger for writing activity logs to PostgreSQL database."""

    def __init__(self):
        """Initialize activity logger with database connection."""
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(self.db_url)
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _ensure_connection(self):
        """Ensure database connection is alive."""
        try:
            if self.conn is None or self.conn.closed:
                self._connect()
            else:
                # Test connection
                with self.conn.cursor() as cur:
                    cur.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Connection lost, reconnecting: {e}")
            self._connect()

    async def log_activity(
        self,
        user_id: str,
        task_id: Optional[int],
        action: str,
        entity_type: str = "task",
        entity_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> int:
        """Log an activity to the database.

        Args:
            user_id: User ID
            task_id: Task ID
            action: Action performed
            entity_type: Type of entity
            entity_id: ID of the entity
            changes: Dictionary of changes
            metadata: Additional metadata
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            ID of the created activity log entry
        """
        self._ensure_connection()

        try:
            with self.conn.cursor() as cur:
                query = """
                    INSERT INTO activity_logs (
                        user_id, task_id, action, entity_type, entity_id,
                        changes, metadata, ip_address, user_agent, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """

                cur.execute(query, (
                    user_id,
                    task_id,
                    action,
                    entity_type,
                    entity_id,
                    Json(changes) if changes else None,
                    Json(metadata) if metadata else None,
                    ip_address,
                    user_agent,
                    datetime.utcnow()
                ))

                activity_id = cur.fetchone()[0]
                self.conn.commit()

                logger.info(f"Logged activity {activity_id}: {action} for task {task_id}")
                return activity_id

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error logging activity: {e}")
            raise

    async def get_user_activities(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """Get activities for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of activity logs
        """
        self._ensure_connection()

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT id, user_id, task_id, action, entity_type, entity_id,
                           changes, metadata, created_at
                    FROM activity_logs
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """

                cur.execute(query, (user_id, limit, offset))
                return cur.fetchall()

        except Exception as e:
            logger.error(f"Error fetching activities: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")
