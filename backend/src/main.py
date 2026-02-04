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

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

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
    """Initialize database on startup."""
    logger.info("Starting up Todo API...")
    try:
        # In serverless, skip DB init to avoid cold start issues
        if not os.getenv("VERCEL"):
            await init_db()
            logger.info("Database initialized successfully")
        else:
            logger.info("Skipping DB init in serverless environment")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Todo API...")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Todo API is running",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from .api.routes import auth, tasks, chat

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/users", tags=["Tasks"])
app.include_router(chat.router, tags=["Chat"])











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
