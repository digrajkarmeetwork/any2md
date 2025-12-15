# Quick Start Guide

## Installation

```bash
# Install with web UI support
pip install ".[web]"

# Or install all dependencies manually
pip install fastapi uvicorn python-multipart mammoth pymupdf openpyxl pyyaml typer rich Pillow
```

## Start the Web UI

**Option 1: Using startup script**
```bash
# Windows
start_web_ui.bat

# macOS/Linux
python start_web_ui.py
```

**Option 2: Using CLI**
```bash
doc2mkdocs serve
```

Then open **http://127.0.0.1:8000** in your browser.

## Using the Web Interface

1. Drag and drop files (DOCX, PDF, XLSX) onto the upload area
2. Wait for validation (green ✓ = ready)
3. Click **"Convert Files"**
4. Review quality scores and warnings
5. Click **"Download ZIP"** to get your converted Markdown files

## Using the CLI

```bash
# Convert a single file
doc2mkdocs convert document.docx --out docs/

# Convert a directory
doc2mkdocs convert ./source-docs --out docs/

# With options
doc2mkdocs convert ./source-docs --out docs/ --mkdocs-nav --pdf-ocr auto
```

## Troubleshooting

**Module not found:**
```bash
pip install fastapi uvicorn python-multipart Pillow
```

**Port already in use:**
```bash
doc2mkdocs serve --port 8001
```

**Python not found (Windows):**
Download from https://www.python.org/downloads/ and check "Add Python to PATH" during installation.

---

For more details, see [README.md](README.md)

