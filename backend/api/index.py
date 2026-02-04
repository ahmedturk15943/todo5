"""Vercel serverless function entry point."""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set environment variables with fallbacks
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://placeholder")
os.environ.setdefault("BETTER_AUTH_SECRET", "placeholder-secret-key-minimum-32-chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRY_DAYS", "7")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ["VERCEL"] = "1"

# Import the main FastAPI app
from src.main import app

# Export for Vercel
app = app
