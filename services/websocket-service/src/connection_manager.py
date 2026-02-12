"""Connection manager for tracking WebSocket connections."""

import logging
from typing import Dict, Set, Optional, Any
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and user-to-socket mappings."""

    def __init__(self):
        """Initialize connection manager."""
        # sid -> connection info (user_id, device_id)
        self.connections: Dict[str, Dict[str, Any]] = {}

        # user_id -> set of sids
        self.user_connections: Dict[str, Set[str]] = {}

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def add_connection(
        self,
        sid: str,
        user_id: str,
        device_id: Optional[str] = None
    ) -> None:
        """Add a new connection.

        Args:
            sid: Socket ID
            user_id: User ID
            device_id: Device ID (optional)
        """
        async with self.lock:
            # Store connection info
            self.connections[sid] = {
                'user_id': user_id,
                'device_id': device_id,
                'connected_at': asyncio.get_event_loop().time()
            }

            # Add to user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(sid)

            logger.info(
                f"Connection added: {sid} (user: {user_id}, device: {device_id}). "
                f"Total connections for user: {len(self.user_connections[user_id])}"
            )

    async def remove_connection(self, sid: str) -> None:
        """Remove a connection.

        Args:
            sid: Socket ID
        """
        async with self.lock:
            if sid not in self.connections:
                return

            connection = self.connections[sid]
            user_id = connection['user_id']

            # Remove from connections
            del self.connections[sid]

            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(sid)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            logger.info(f"Connection removed: {sid} (user: {user_id})")

    async def get_connection(self, sid: str) -> Optional[Dict[str, Any]]:
        """Get connection info by socket ID.

        Args:
            sid: Socket ID

        Returns:
            Connection info or None
        """
        return self.connections.get(sid)

    async def get_user_connections(self, user_id: str) -> Set[str]:
        """Get all socket IDs for a user.

        Args:
            user_id: User ID

        Returns:
            Set of socket IDs
        """
        return self.user_connections.get(user_id, set()).copy()

    async def get_connection_count(self) -> int:
        """Get total number of active connections.

        Returns:
            Connection count
        """
        return len(self.connections)

    async def get_user_count(self) -> int:
        """Get total number of connected users.

        Returns:
            User count
        """
        return len(self.user_connections)

    async def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections.

        Args:
            user_id: User ID

        Returns:
            True if user is connected
        """
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0

    async def get_device_sid(self, user_id: str, device_id: str) -> Optional[str]:
        """Get socket ID for a specific device.

        Args:
            user_id: User ID
            device_id: Device ID

        Returns:
            Socket ID or None
        """
        if user_id not in self.user_connections:
            return None

        for sid in self.user_connections[user_id]:
            connection = self.connections.get(sid)
            if connection and connection.get('device_id') == device_id:
                return sid

        return None
