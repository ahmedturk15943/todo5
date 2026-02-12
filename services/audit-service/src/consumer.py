"""Kafka consumer for audit logging."""

import os
import logging
import json
import asyncio
from typing import Optional
from aiokafka import AIOKafkaConsumer
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

logger = logging.getLogger(__name__)


class AuditConsumer:
    """Consumer for task-events topic that logs activities to database."""

    def __init__(self, logger_service):
        """Initialize audit consumer.

        Args:
            logger_service: ActivityLogger instance for database operations
        """
        self.logger_service = logger_service
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

        # Kafka configuration
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = 'task-events'
        self.group_id = 'audit-service'

    async def start(self):
        """Start consuming messages from Kafka."""
        try:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
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
        """Process a task event and log to database.

        Args:
            event: Task event data
        """
        try:
            event_type = event.get('event_type')
            task_id = event.get('task_id')
            user_id = event.get('user_id')
            task_data = event.get('task_data', {})

            logger.info(f"Processing {event_type} for task {task_id} (user: {user_id})")

            # Map event type to activity action
            action_map = {
                'created': 'created',
                'updated': 'updated',
                'completed': 'completed',
                'deleted': 'deleted'
            }

            action = action_map.get(event_type, 'updated')

            # Extract changes if available
            changes = None
            if event_type == 'updated' and 'changes' in event:
                changes = event['changes']

            # Log activity to database
            await self.logger_service.log_activity(
                user_id=user_id,
                task_id=task_id,
                action=action,
                entity_type='task',
                entity_id=task_id,
                changes=changes,
                metadata={
                    'event_id': event.get('event_id'),
                    'timestamp': event.get('timestamp'),
                    'source': 'kafka'
                }
            )

            logger.info(f"Logged {action} activity for task {task_id}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
