"""Main entry point for audit service."""

import os
import logging
import asyncio
from .consumer import AuditConsumer
from .logger import ActivityLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start audit service."""
    logger.info("Starting Audit Service...")

    # Initialize activity logger
    activity_logger = ActivityLogger()

    # Initialize consumer
    consumer = AuditConsumer(activity_logger)

    try:
        # Start consuming
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Cleanup
        await consumer.stop()
        activity_logger.close()
        logger.info("Audit Service stopped")


if __name__ == "__main__":
    asyncio.run(main())
