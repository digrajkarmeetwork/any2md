#!/usr/bin/env python3
"""
Quick start script for doc2mkdocs web UI.

This script starts the web server without requiring installation.
"""

import sys
import site
from pathlib import Path

# Add user site-packages to path (for user installations)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Add src to path so we can import without installing
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import uvicorn
    from doc2mkdocs.web import create_app
except ImportError as e:
    print("❌ Missing dependencies!")
    print(f"\nError: {e}")
    print("\nPlease install web dependencies:")
    print("  python -m pip install fastapi uvicorn python-multipart")
    print("\nOr install the full package:")
    print('  python -m pip install -e ".[web]"')
    print("\nNote: Make sure to use 'python -m pip' instead of just 'pip'")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting doc2mkdocs Web UI...")
    print("📂 Open your browser to: http://127.0.0.1:8000")
    print("⏹️  Press CTRL+C to stop\n")

    # Create app
    app = create_app()

    # Run server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )

