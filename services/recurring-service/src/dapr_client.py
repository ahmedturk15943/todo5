"""Dapr client for recurring task service."""

import httpx
from typing import Dict, Any


class DaprClient:
    """Dapr client for recurring task service."""

    def __init__(self, dapr_port: int = 3500):
        """Initialize Dapr client.

        Args:
            dapr_port: Dapr sidecar port
        """
        self.dapr_url = f"http://localhost:{dapr_port}"

    async def publish_event(self, topic: str, data: Dict[str, Any]) -> bool:
        """Publish event to Kafka via Dapr.

        Args:
            topic: Topic name
            data: Event data

        Returns:
            True if published successfully
        """
        url = f"{self.dapr_url}/v1.0/publish/pubsub/{topic}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=5.0)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Failed to publish event: {e}")
            return False
