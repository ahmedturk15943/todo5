"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound
import logging

from .config import settings
from .api.middleware import (
    validation_exception_handler,
    integrity_error_handler,
    not_found_handler,
    generic_exception_handler,
)
from .db import init_db
from .dapr import DaprPubSubClient, DaprStateClient, DaprJobsClient, DaprSecretsClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize Dapr clients (global instances)
dapr_pubsub = DaprPubSubClient()
dapr_state = DaprStateClient()
dapr_jobs = DaprJobsClient()
dapr_secrets = DaprSecretsClient()

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo application",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(NoResultFound, not_found_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.on_event("startup")
async def startup_event():
    """Initialize database and Dapr clients on startup."""
    logger.info("Starting up Todo API (Phase 5 - Event-Driven Architecture)...")
    try:
        # In serverless, skip DB init to avoid cold start issues
        if not os.getenv("VERCEL"):
            await init_db()
            logger.info("Database initialized successfully")
        else:
            logger.info("Skipping DB init in serverless environment")

        # Initialize Dapr clients
        logger.info("Dapr clients initialized:")
        logger.info(f"  - Pub/Sub: {dapr_pubsub.pubsub_name}")
        logger.info(f"  - State Store: {dapr_state.store_name}")
        logger.info(f"  - Jobs API: enabled")
        logger.info(f"  - Secrets Store: {dapr_secrets.store_name}")

    except Exception as e:
        logger.warning(f"Initialization warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Todo API...")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Todo API is running",
        "version": "5.0.0",
        "phase": "Phase 5 - Advanced Cloud Deployment",
        "features": [
            "Recurring Tasks",
            "Smart Reminders",
            "Priorities & Tags",
            "Advanced Search",
            "Real-Time Sync",
            "Activity History",
            "Event-Driven Architecture (Kafka + Dapr)"
        ],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from .api.routes import auth, tasks, recurring, reminders, tags, search, activity

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/users", tags=["Tasks"])
app.include_router(recurring.router, prefix="/api", tags=["Recurring Tasks"])
app.include_router(reminders.router, prefix="/api", tags=["Reminders"])
app.include_router(tags.router, prefix="/api", tags=["Tags"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(activity.router, prefix="/api", tags=["Activity"])

# Chat router - optional, only load if dependencies are available
try:
    from .api.routes import chat
    app.include_router(chat.router, tags=["Chat"])
    logger.info("Chat router loaded successfully")
except Exception as e:
    logger.warning(f"Chat router not loaded: {e}")











# from pydantic_settings import BaseSettings, SettingsConfigDict
# from typing import List
# import os
# from dotenv import load_dotenv

# # Load .env early so all subprocesses can see variables
# load_dotenv()

# class Settings(BaseSettings):
#     """Application settings loaded from environment variables."""

#     database_url: str
#     openai_api_key: str
#     better_auth_secret: str
#     jwt_algorithm: str = "HS256"
#     jwt_expiry_days: int = 7
#     cors_origins: str = "http://localhost:3000"
#     debug: bool = False
#     log_level: str = "INFO"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=False,
#     )

#     @property
#     def cors_origins_list(self) -> List[str]:
#         return [origin.strip() for origin in self.cors_origins.split(",")]

# # Global settings instance
# settings = Settings()

# # Optional: quick check
# if not settings.openai_api_key:
#     raise ValueError("OPENAI_API_KEY not set in .env")
