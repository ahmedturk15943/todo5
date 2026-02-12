"""Notification consumer for processing reminder events."""

import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session, create_engine

logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Consumer for reminders topic to send notifications."""

    def __init__(self, kafka_brokers: str, database_url: str):
        """Initialize notification consumer.

        Args:
            kafka_brokers: Kafka broker addresses
            database_url: Database connection string
        """
        self.kafka_brokers = kafka_brokers
        self.database_url = database_url
        self.consumer = None
        self.engine = None

    async def start(self):
        """Start consuming reminder events."""
        # Initialize Kafka consumer
        self.consumer = AIOKafkaConsumer(
            'reminders',
            bootstrap_servers=self.kafka_brokers,
            group_id='notification-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )

        # Initialize database engine
        self.engine = create_engine(self.database_url)

        await self.consumer.start()
        logger.info("Notification Service started, consuming from reminders topic")

        try:
            async for message in self.consumer:
                await self.process_event(message.value)
        finally:
            await self.consumer.stop()

    async def process_event(self, event: dict):
        """Process reminder event and send notification.

        Args:
            event: Reminder event from Kafka
        """
        try:
            event_type = event.get('event_type')
            reminder_id = event.get('reminder_id')
            task_id = event.get('task_id')
            user_id = event.get('user_id')

            # Only process due reminders
            if event_type != 'reminder.due':
                return

            logger.info(f"Processing reminder {reminder_id} for task {task_id}")

            # Send notification
            await self.send_notification(reminder_id, task_id, user_id)

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)

    async def send_notification(self, reminder_id: int, task_id: int, user_id: str):
        """Send notification for reminder.

        Args:
            reminder_id: Reminder ID
            task_id: Task ID
            user_id: User ID
        """
        from backend.src.models import Reminder, Task
        from backend.src.services.notification_service import NotificationService

        with Session(self.engine) as session:
            # Get reminder and task
            reminder = session.get(Reminder, reminder_id)
            task = session.get(Task, task_id)

            if not reminder or not task:
                logger.warning(f"Reminder {reminder_id} or task {task_id} not found")
                return

            # Send notification
            notification_service = NotificationService()
            success = await notification_service.send_reminder(reminder, task)

            if success:
                logger.info(f"Notification sent for reminder {reminder_id}")
            else:
                logger.error(f"Failed to send notification for reminder {reminder_id}")
