"""Broadcaster for sending updates to WebSocket clients."""

import os
import logging
from typing import Optional, Any, Dict
import json
import asyncio
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class Broadcaster:
    """Broadcasts task updates to connected WebSocket clients using Redis Pub/Sub."""

    def __init__(self, connection_manager, sio):
        """Initialize broadcaster.

        Args:
            connection_manager: ConnectionManager instance
            sio: Socket.IO server instance
        """
        self.connection_manager = connection_manager
        self.sio = sio
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'

        if self.redis_enabled:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            logger.info(f"Redis Pub/Sub enabled: {redis_url}")
        else:
            logger.info("Redis Pub/Sub disabled (single instance mode)")

    async def broadcast_to_user(
        self,
        user_id: str,
        event_type: str,
        data: Dict[str, Any],
        exclude_device_id: Optional[str] = None
    ):
        """Broadcast an update to all of a user's connected devices.

        Args:
            user_id: User ID to broadcast to
            event_type: Type of event (task.created, task.updated, etc.)
            data: Event data
            exclude_device_id: Device ID to exclude (to avoid echo)
        """
        try:
            # Get all connections for this user
            sids = await self.connection_manager.get_user_connections(user_id)

            if not sids:
                logger.debug(f"No connections found for user {user_id}")
                return

            # Filter out the source device if specified
            if exclude_device_id:
                filtered_sids = []
                for sid in sids:
                    connection = await self.connection_manager.get_connection(sid)
                    if connection and connection.get('device_id') != exclude_device_id:
                        filtered_sids.append(sid)
                sids = filtered_sids

            if not sids:
                logger.debug(f"No target connections after filtering for user {user_id}")
                return

            # Prepare message
            message = {
                'type': event_type,
                'data': data
            }

            # Send to all target connections
            for sid in sids:
                try:
                    await self.sio.emit('task_update', message, room=sid)
                    logger.debug(f"Sent {event_type} to {sid}")
                except Exception as e:
                    logger.error(f"Error sending to {sid}: {e}")

            logger.info(
                f"Broadcasted {event_type} to {len(sids)} connections "
                f"for user {user_id}"
            )

            # If Redis is enabled, publish to Redis for other instances
            if self.redis_enabled and self.redis_client:
                await self._publish_to_redis(user_id, event_type, data, exclude_device_id)

        except Exception as e:
            logger.error(f"Error broadcasting to user {user_id}: {e}")

    async def _publish_to_redis(
        self,
        user_id: str,
        event_type: str,
        data: Dict[str, Any],
        exclude_device_id: Optional[str] = None
    ):
        """Publish update to Redis for other WebSocket instances.

        Args:
            user_id: User ID
            event_type: Event type
            data: Event data
            exclude_device_id: Device ID to exclude
        """
        try:
            message = {
                'user_id': user_id,
                'event_type': event_type,
                'data': data,
                'exclude_device_id': exclude_device_id
            }

            channel = f"websocket:user:{user_id}"
            await self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Published to Redis channel: {channel}")

        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")

    async def start_redis_subscriber(self):
        """Start Redis subscriber for receiving updates from other instances."""
        if not self.redis_enabled or not self.redis_client:
            return

        try:
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.psubscribe('websocket:user:*')
            logger.info("Started Redis subscriber")

            # Start listening loop
            asyncio.create_task(self._redis_listen_loop())

        except Exception as e:
            logger.error(f"Error starting Redis subscriber: {e}")

    async def _redis_listen_loop(self):
        """Listen for messages from Redis."""
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'pmessage':
                    try:
                        data = json.loads(message['data'])
                        await self._handle_redis_message(data)
                    except Exception as e:
                        logger.error(f"Error handling Redis message: {e}")

        except Exception as e:
            logger.error(f"Error in Redis listen loop: {e}")

    async def _handle_redis_message(self, message: Dict[str, Any]):
        """Handle a message received from Redis.

        Args:
            message: Message data from Redis
        """
        try:
            user_id = message['user_id']
            event_type = message['event_type']
            data = message['data']
            exclude_device_id = message.get('exclude_device_id')

            # Broadcast to local connections only (don't re-publish to Redis)
            await self.broadcast_to_user(
                user_id=user_id,
                event_type=event_type,
                data=data,
                exclude_device_id=exclude_device_id
            )

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    async def close(self):
        """Close Redis connections."""
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

        logger.info("Broadcaster closed")
