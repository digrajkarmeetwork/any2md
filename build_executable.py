"""Build standalone executable using PyInstaller.

Usage:
    python build_executable.py

This will create a standalone executable in the dist/ directory.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def build_executable() -> None:
    """Build standalone executable using PyInstaller."""
    print("Building doc2mkdocs executable...")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Determine platform-specific settings
    system = platform.system()
    exe_name = "doc2mkdocs"
    if system == "Windows":
        exe_name += ".exe"

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", "doc2mkdocs",
        "--onefile",
        "--console",
        "--clean",
        # Entry point
        "src/doc2mkdocs/__main__.py",
        # Hidden imports
        "--hidden-import", "doc2mkdocs.converters.docx_converter",
        "--hidden-import", "doc2mkdocs.converters.pdf_converter",
        "--hidden-import", "doc2mkdocs.converters.xlsx_converter",
        "--hidden-import", "mammoth",
        "--hidden-import", "fitz",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pytesseract",
        # Collect data files
        "--collect-all", "mammoth",
        "--collect-all", "openpyxl",
    ]

    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    # Check output
    dist_dir = Path("dist")
    exe_path = dist_dir / exe_name

    if exe_path.exists():
        print(f"\n✓ Executable built successfully: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        print("\nYou can now distribute this executable.")
        print("Note: Users will still need Tesseract and Pandoc installed for full functionality.")
    else:
        print("\n✗ Build failed - executable not found")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()

