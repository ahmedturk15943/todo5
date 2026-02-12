"""Kafka consumer for task-updates topic."""

import os
import logging
import json
import asyncio
from typing import Optional
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class TaskUpdatesConsumer:
    """Consumer for task-updates topic that broadcasts to WebSocket clients."""

    def __init__(self, broadcaster):
        """Initialize task updates consumer.

        Args:
            broadcaster: Broadcaster instance for sending updates to clients
        """
        self.broadcaster = broadcaster
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

        # Kafka configuration
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = 'task-updates'
        self.group_id = 'websocket-service'

    async def start(self):
        """Start consuming messages from Kafka."""
        try:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )

            await self.consumer.start()
            self.running = True
            logger.info(f"Started consuming from topic: {self.topic}")

            # Start consuming loop
            await self._consume_loop()

        except Exception as e:
            logger.error(f"Error starting consumer: {e}")
            raise

    async def stop(self):
        """Stop consuming messages."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Consumer stopped")

    async def _consume_loop(self):
        """Main consumption loop."""
        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    await self._process_message(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue processing other messages

        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
        finally:
            logger.info("Consume loop ended")

    async def _process_message(self, event: dict):
        """Process a task update event.

        Args:
            event: Task update event data
        """
        try:
            event_type = event.get('event_type')
            user_id = event.get('user_id')
            task_id = event.get('task_id')
            source_device_id = event.get('source_device_id')

            logger.info(
                f"Processing {event_type} for task {task_id} "
                f"(user: {user_id}, source: {source_device_id})"
            )

            # Broadcast to all user's devices (except source device to avoid echo)
            await self.broadcaster.broadcast_to_user(
                user_id=user_id,
                event_type=event_type,
                data=event,
                exclude_device_id=source_device_id
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
