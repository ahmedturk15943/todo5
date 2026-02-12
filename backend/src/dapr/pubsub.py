"""Dapr Pub/Sub client wrapper for event publishing and subscription."""

import httpx
import json
from typing import Any, Dict, Optional
from datetime import datetime


class DaprPubSubClient:
    """Client for Dapr Pub/Sub component."""

    def __init__(self, dapr_port: int = 3500, pubsub_name: str = "pubsub"):
        """Initialize Dapr Pub/Sub client.

        Args:
            dapr_port: Dapr sidecar HTTP port (default: 3500)
            pubsub_name: Name of Dapr Pub/Sub component (default: "pubsub")
        """
        self.dapr_url = f"http://localhost:{dapr_port}"
        self.pubsub_name = pubsub_name

    async def publish(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Publish event to Kafka topic via Dapr.

        Args:
            topic: Kafka topic name (e.g., "task-events", "reminders", "task-updates")
            data: Event payload as dictionary
            metadata: Optional metadata for the event

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        payload = {
            "data": data,
            "metadata": metadata or {}
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Failed to publish to topic {topic}: {e}")
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish task event to task-events topic.

        Args:
            event_type: Type of event (created, updated, completed, deleted)
            task_id: Task ID
            user_id: User ID
            task_data: Full task object

        Returns:
            True if published successfully
        """
        event = {
            "schema_version": "1.0",
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "task_data": task_data,
            "metadata": {}
        }

        return await self.publish("task-events", event)

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: str,
        remind_at: str,
        reminder_id: int
    ) -> bool:
        """Publish reminder event to reminders topic.

        Args:
            task_id: Task ID
            user_id: User ID
            remind_at: ISO format datetime when reminder should fire
            reminder_id: Reminder ID

        Returns:
            True if published successfully
        """
        event = {
            "schema_version": "1.0",
            "event_type": "reminder.scheduled",
            "reminder_id": reminder_id,
            "task_id": task_id,
            "user_id": user_id,
            "remind_at": remind_at,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self.publish("reminders", event)

    async def publish_update_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        changes: Dict[str, Any]
    ) -> bool:
        """Publish real-time update event to task-updates topic.

        Args:
            event_type: Type of update (task.created, task.updated, task.deleted)
            task_id: Task ID
            user_id: User ID
            changes: What changed

        Returns:
            True if published successfully
        """
        event = {
            "schema_version": "1.0",
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "changes": changes
        }

        return await self.publish("task-updates", event)
