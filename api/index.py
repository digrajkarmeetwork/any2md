"""
Vercel serverless function entry point for doc2mkdocs web UI.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from doc2mkdocs.web import create_app

# Create the FastAPI app
app = create_app()

# Vercel expects the app to be named 'app'
# This will be used as the ASGI application

