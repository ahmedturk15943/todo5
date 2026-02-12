"""Main entry point for Notification Service."""

import asyncio
import logging
from consumer import NotificationConsumer
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Start the notification service."""
    logger.info("Starting Notification Service...")

    kafka_brokers = os.getenv('KAFKA_BROKERS', 'todo-kafka-kafka-bootstrap:9092')
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    consumer = NotificationConsumer(kafka_brokers, database_url)

    try:
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Notification Service...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    asyncio.run(main())
