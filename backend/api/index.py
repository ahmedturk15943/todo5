"""Vercel serverless function entry point."""

import sys
from pathlib import Path

# Add src directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app

# Export the app for Vercel
handler = app
