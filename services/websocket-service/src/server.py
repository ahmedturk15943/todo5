"""WebSocket server for real-time task synchronization."""

import os
import logging
from typing import Dict, Any
import socketio
from aiohttp import web
import asyncio

from .connection_manager import ConnectionManager
from .consumer import TaskUpdatesConsumer
from .broadcaster import Broadcaster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='aiohttp',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create aiohttp app
app = web.Application()
sio.attach(app)

# Initialize components
connection_manager = ConnectionManager()
broadcaster = Broadcaster(connection_manager, sio)
consumer = None  # Will be initialized in startup


@sio.event
async def connect(sid: str, environ: Dict[str, Any], auth: Dict[str, Any]):
    """Handle client connection.

    Args:
        sid: Socket ID
        environ: WSGI environment
        auth: Authentication data containing user_id and device_id
    """
    try:
        user_id = auth.get('user_id')
        device_id = auth.get('device_id')

        if not user_id:
            logger.warning(f"Connection rejected for {sid}: missing user_id")
            return False

        # Register connection
        await connection_manager.add_connection(sid, user_id, device_id)

        # Join user-specific room
        await sio.enter_room(sid, f"user:{user_id}")

        logger.info(f"Client connected: {sid} (user: {user_id}, device: {device_id})")

        # Send connection confirmation
        await sio.emit('connected', {
            'message': 'Connected to real-time sync',
            'device_id': device_id
        }, room=sid)

        return True

    except Exception as e:
        logger.error(f"Error handling connection: {e}")
        return False


@sio.event
async def disconnect(sid: str):
    """Handle client disconnection.

    Args:
        sid: Socket ID
    """
    try:
        connection = await connection_manager.get_connection(sid)
        if connection:
            user_id = connection.get('user_id')
            device_id = connection.get('device_id')
            logger.info(f"Client disconnected: {sid} (user: {user_id}, device: {device_id})")

        await connection_manager.remove_connection(sid)

    except Exception as e:
        logger.error(f"Error handling disconnection: {e}")


@sio.event
async def ping(sid: str):
    """Handle ping from client.

    Args:
        sid: Socket ID
    """
    await sio.emit('pong', room=sid)


async def start_consumer(app):
    """Start Kafka consumer on app startup."""
    global consumer

    try:
        consumer = TaskUpdatesConsumer(broadcaster)
        asyncio.create_task(consumer.start())
        logger.info("Task updates consumer started")
    except Exception as e:
        logger.error(f"Failed to start consumer: {e}")


async def stop_consumer(app):
    """Stop Kafka consumer on app shutdown."""
    global consumer

    if consumer:
        await consumer.stop()
        logger.info("Task updates consumer stopped")


# Register startup/shutdown handlers
app.on_startup.append(start_consumer)
app.on_shutdown.append(stop_consumer)


@app.route('/')
async def health_check(request):
    """Health check endpoint."""
    return web.json_response({
        'status': 'healthy',
        'service': 'websocket-service',
        'connections': await connection_manager.get_connection_count()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8001))
    web.run_app(app, host='0.0.0.0', port=port)
