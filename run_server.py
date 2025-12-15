"""Simple server runner with better error handling."""
import sys
import site
from pathlib import Path

# Add user site-packages
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("  doc2mkdocs Web UI Server")
print("=" * 60)
print()

# Import and run
try:
    print("Loading FastAPI...")
    import uvicorn
    print("✅ FastAPI loaded")
    
    print("Loading doc2mkdocs web app...")
    from doc2mkdocs.web import create_app
    print("✅ Web app loaded")
    
    print()
    print("🚀 Starting server...")
    print("📂 URL: http://127.0.0.1:8000")
    print("⏹️  Press CTRL+C to stop")
    print()
    print("-" * 60)
    
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print()
    print("Missing dependencies. Install with:")
    print("  python -m pip install fastapi uvicorn python-multipart Pillow")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

