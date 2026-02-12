"""Task event producer for publishing task events to Kafka."""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from ...dapr import DaprPubSubClient
from ..schemas.task_event import TaskEvent
from ..schemas.update_event import UpdateEvent


class TaskEventProducer:
    """Producer for task events."""

    def __init__(self, pubsub_client: DaprPubSubClient):
        """Initialize task event producer.

        Args:
            pubsub_client: Dapr Pub/Sub client
        """
        self.pubsub = pubsub_client

    async def publish_task_created(
        self,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any],
        source_device_id: Optional[str] = None
    ) -> bool:
        """Publish task created event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Full task object
            source_device_id: Device ID that originated the change

        Returns:
            True if published successfully
        """
        # Publish to task-events for recurring service
        event = TaskEvent(
            event_type="created",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )
        await self.pubsub.publish("task-events", event.model_dump())

        # Publish to task-updates for real-time sync
        update_event = UpdateEvent(
            event_type="task.created",
            task_id=uuid.UUID(str(task_id)) if not isinstance(task_id, uuid.UUID) else task_id,
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            task_data=task_data,
            version=task_data.get("version", 1),
            source_device_id=source_device_id
        )
        return await self.pubsub.publish("task-updates", update_event.model_dump())

    async def publish_task_updated(
        self,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any],
        changes: Optional[Dict[str, Any]] = None,
        source_device_id: Optional[str] = None
    ) -> bool:
        """Publish task updated event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Full task object
            changes: Dictionary of changed fields
            source_device_id: Device ID that originated the change

        Returns:
            True if published successfully
        """
        # Publish to task-events for recurring service
        event = TaskEvent(
            event_type="updated",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )
        await self.pubsub.publish("task-events", event.model_dump())

        # Publish to task-updates for real-time sync
        update_event = UpdateEvent(
            event_type="task.updated",
            task_id=uuid.UUID(str(task_id)) if not isinstance(task_id, uuid.UUID) else task_id,
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            changes=changes,
            task_data=task_data,
            version=task_data.get("version", 1),
            source_device_id=source_device_id
        )
        return await self.pubsub.publish("task-updates", update_event.model_dump())

    async def publish_task_completed(
        self,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any],
        source_device_id: Optional[str] = None
    ) -> bool:
        """Publish task completed event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Full task object
            source_device_id: Device ID that originated the change

        Returns:
            True if published successfully
        """
        # Publish to task-events for recurring service
        event = TaskEvent(
            event_type="completed",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )
        await self.pubsub.publish("task-events", event.model_dump())

        # Publish to task-updates for real-time sync
        update_event = UpdateEvent(
            event_type="task.completed",
            task_id=uuid.UUID(str(task_id)) if not isinstance(task_id, uuid.UUID) else task_id,
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            changes={"status": "complete"},
            task_data=task_data,
            version=task_data.get("version", 1),
            source_device_id=source_device_id
        )
        return await self.pubsub.publish("task-updates", update_event.model_dump())

    async def publish_task_deleted(
        self,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any],
        source_device_id: Optional[str] = None
    ) -> bool:
        """Publish task deleted event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Full task object
            source_device_id: Device ID that originated the change

        Returns:
            True if published successfully
        """
        # Publish to task-events for recurring service
        event = TaskEvent(
            event_type="deleted",
            task_id=task_id,
            user_id=user_id,
            task_data=task_data
        )
        await self.pubsub.publish("task-events", event.model_dump())

        # Publish to task-updates for real-time sync
        update_event = UpdateEvent(
            event_type="task.deleted",
            task_id=uuid.UUID(str(task_id)) if not isinstance(task_id, uuid.UUID) else task_id,
            user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
            task_data=task_data,
            version=task_data.get("version", 1),
            source_device_id=source_device_id
        )
        return await self.pubsub.publish("task-updates", update_event.model_dump())
