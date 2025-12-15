#!/usr/bin/env python3
"""
Check if all dependencies for doc2mkdocs web UI are installed.
"""

import sys

def check_module(module_name, package_name=None):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False

def main():
    print("=" * 50)
    print("  doc2mkdocs Web UI - Dependency Check")
    print("=" * 50)
    print()
    
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro}")
        print("   Required: Python 3.11+")
        print()
        return False
    
    print()
    print("Checking required dependencies...")
    
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("multipart", "python-multipart"),
    ]
    
    all_installed = True
    for module, package in required:
        if not check_module(module, package):
            all_installed = False
    
    print()
    print("Checking optional dependencies...")
    
    optional = [
        ("mammoth", "mammoth"),
        ("fitz", "pymupdf"),
        ("openpyxl", "openpyxl"),
        ("yaml", "pyyaml"),
        ("typer", "typer"),
        ("rich", "rich"),
    ]
    
    for module, package in optional:
        check_module(module, package)
    
    print()
    print("=" * 50)
    
    if all_installed:
        print("✅ All required dependencies are installed!")
        print()
        print("You can start the web UI with:")
        print("  python start_web_ui.py")
        print()
        print("Or:")
        print("  doc2mkdocs serve")
        print()
        return True
    else:
        print("❌ Some required dependencies are missing!")
        print()
        print("Install them with:")
        print('  pip install fastapi uvicorn python-multipart')
        print()
        print("Or install everything:")
        print('  pip install -e ".[web]"')
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

