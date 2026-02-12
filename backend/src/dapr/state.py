"""Dapr State Store client wrapper for persistent state management."""

import httpx
import json
from typing import Any, Dict, List, Optional


class DaprStateClient:
    """Client for Dapr State Store component."""

    def __init__(self, dapr_port: int = 3500, store_name: str = "statestore"):
        """Initialize Dapr State Store client.

        Args:
            dapr_port: Dapr sidecar HTTP port (default: 3500)
            store_name: Name of Dapr State Store component (default: "statestore")
        """
        self.dapr_url = f"http://localhost:{dapr_port}"
        self.store_name = store_name

    async def save(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Save state to Dapr state store.

        Args:
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional metadata (e.g., ttlInSeconds)

        Returns:
            True if saved successfully
        """
        url = f"{self.dapr_url}/v1.0/state/{self.store_name}"

        payload = [{
            "key": key,
            "value": value,
            "metadata": metadata or {}
        }]

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
            print(f"Failed to save state for key {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get state from Dapr state store.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        url = f"{self.dapr_url}/v1.0/state/{self.store_name}/{key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)

                if response.status_code == 204:
                    return None

                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Failed to get state for key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete state from Dapr state store.

        Args:
            key: State key

        Returns:
            True if deleted successfully
        """
        url = f"{self.dapr_url}/v1.0/state/{self.store_name}/{key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, timeout=5.0)
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            print(f"Failed to delete state for key {key}: {e}")
            return False

    async def save_conversation_state(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]]
    ) -> bool:
        """Save conversation state for AI chatbot.

        Args:
            conversation_id: Conversation ID
            messages: List of messages in conversation

        Returns:
            True if saved successfully
        """
        key = f"conversation-{conversation_id}"
        value = {"messages": messages}
        return await self.save(key, value)

    async def get_conversation_state(
        self,
        conversation_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get conversation state for AI chatbot.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of messages or None if not found
        """
        key = f"conversation-{conversation_id}"
        state = await self.get(key)

        if state and "messages" in state:
            return state["messages"]
        return None
