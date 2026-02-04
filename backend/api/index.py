"""Vercel serverless function - Final diagnostic."""

import sys
import os
import traceback
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://placeholder")
os.environ.setdefault("BETTER_AUTH_SECRET", "placeholder-secret-key-minimum-32-chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRY_DAYS", "7")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ["VERCEL"] = "1"

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    result = {"status": "diagnostic"}

    # Test each import step by step
    try:
        from src.config import settings
        result["config"] = "OK"
        result["debug_value"] = str(settings.debug)
        result["debug_type"] = str(type(settings.debug))
    except Exception as e:
        result["config"] = f"FAILED: {str(e)}"
        result["config_trace"] = traceback.format_exc()
        return result

    try:
        from src.db import init_db
        result["db_module"] = "OK"
    except Exception as e:
        result["db_module"] = f"FAILED: {str(e)}"
        result["db_trace"] = traceback.format_exc()
        return result

    try:
        from src.api.middleware import validation_exception_handler
        result["middleware"] = "OK"
    except Exception as e:
        result["middleware"] = f"FAILED: {str(e)}"
        result["middleware_trace"] = traceback.format_exc()
        return result

    try:
        from src.api.routes import auth
        result["auth_router"] = "OK"
    except Exception as e:
        result["auth_router"] = f"FAILED: {str(e)}"
        result["auth_trace"] = traceback.format_exc()
        return result

    try:
        from src.api.routes import tasks
        result["tasks_router"] = "OK"
    except Exception as e:
        result["tasks_router"] = f"FAILED: {str(e)}"
        result["tasks_trace"] = traceback.format_exc()
        return result

    try:
        from src.main import app as main_app
        result["main_app"] = "OK"
    except Exception as e:
        result["main_app"] = f"FAILED: {str(e)}"
        result["main_trace"] = traceback.format_exc()
        return result

    result["all_imports"] = "SUCCESS"
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}
