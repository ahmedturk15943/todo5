"""Recurring Task Service - Microservice for spawning next task occurrences."""

import asyncio
import json
import os
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session, create_engine, select
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RecurringTaskConsumer:
    """Consumer for task-events topic to spawn recurring tasks."""

    def __init__(self, kafka_brokers: str, database_url: str):
        """Initialize recurring task consumer.

        Args:
            kafka_brokers: Kafka broker addresses
            database_url: Database connection string
        """
        self.kafka_brokers = kafka_brokers
        self.database_url = database_url
        self.consumer = None
        self.engine = None

    async def start(self):
        """Start consuming task events."""
        # Initialize Kafka consumer
        self.consumer = AIOKafkaConsumer(
            'task-events',
            bootstrap_servers=self.kafka_brokers,
            group_id='recurring-task-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )

        # Initialize database engine
        self.engine = create_engine(self.database_url)

        await self.consumer.start()
        logger.info("Recurring Task Service started, consuming from task-events topic")

        try:
            async for message in self.consumer:
                await self.process_event(message.value)
        finally:
            await self.consumer.stop()

    async def process_event(self, event: dict):
        """Process task event and spawn next occurrence if needed.

        Args:
            event: Task event from Kafka
        """
        try:
            event_type = event.get('event_type')
            task_data = event.get('task_data', {})
            task_id = event.get('task_id')

            # Only process completed tasks
            if event_type != 'completed':
                return

            # Check if task has recurring pattern
            recurring_pattern_id = task_data.get('recurring_pattern_id')
            if not recurring_pattern_id:
                return

            logger.info(f"Processing completed recurring task {task_id}, pattern {recurring_pattern_id}")

            # Spawn next occurrence
            await self.spawn_next_occurrence(task_id, recurring_pattern_id, task_data)

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)

    async def spawn_next_occurrence(self, task_id: int, pattern_id: int, task_data: dict):
        """Spawn next occurrence of recurring task.

        Args:
            task_id: Completed task ID
            pattern_id: Recurring pattern ID
            task_data: Task data
        """
        # Import here to avoid circular imports
        from backend.src.models import Task, RecurringPattern, TaskStatus
        from backend.src.services.recurring_service import RecurringService

        with Session(self.engine) as session:
            # Get recurring pattern
            pattern = session.get(RecurringPattern, pattern_id)
            if not pattern or not pattern.is_active:
                logger.info(f"Pattern {pattern_id} not active, skipping spawn")
                return

            # Get completed task
            task = session.get(Task, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return

            # Use RecurringService to spawn next occurrence
            service = RecurringService(session)
            new_task = await service.spawn_next_occurrence(task, pattern)

            if new_task:
                logger.info(f"Spawned next occurrence: task {new_task.id} due at {new_task.due_date}")
            else:
                logger.info(f"Pattern {pattern_id} ended, no more occurrences")


async def main():
    """Main entry point for recurring task service."""
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092')
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/todo')

    consumer = RecurringTaskConsumer(kafka_brokers, database_url)
    await consumer.start()


if __name__ == '__main__':
    asyncio.run(main())
