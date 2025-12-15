# Repository Structure

This document describes the clean, organized structure of the doc2mkdocs repository.

## Root Files

- **README.md** - Main documentation with features, installation, and usage
- **QUICK_START.md** - Quick start guide for CLI and Web UI
- **CHANGELOG.md** - Version history and changes
- **LICENSE** - MIT License
- **pyproject.toml** - Python package configuration and dependencies
- **setup.py** - Package setup script
- **start_web_ui.py** - Quick startup script for web UI (Python)
- **start_web_ui.bat** - Quick startup script for web UI (Windows batch)
- **.gitignore** - Git ignore rules

## Source Code (`src/doc2mkdocs/`)

### Core Modules
- **cli.py** - Command-line interface (Typer-based)
- **__init__.py** - Package initialization
- **__main__.py** - Entry point for `python -m doc2mkdocs`

### Converters (`converters/`)
- **docx_converter.py** - DOCX to Markdown converter (Pandoc/Mammoth)
- **pdf_converter.py** - PDF to Markdown converter (PyMuPDF + OCR)
- **xlsx_converter.py** - Excel to Markdown converter (openpyxl)

### Core (`core/`)
- **base_converter.py** - Abstract base class for converters
- **config.py** - Configuration classes and options
- **report.py** - Conversion reporting and quality scoring

### Normalizer (`normalizer/`)
- **markdown_normalizer.py** - Markdown normalization (headings, whitespace)
- **image_handler.py** - Image extraction and path management
- **link_rewriter.py** - Internal link rewriting for MkDocs

### Utils (`utils/`)
- **filename_sanitizer.py** - Filename sanitization utilities
- **logger.py** - Logging configuration

### Web UI (`web/`)
- **app.py** - FastAPI application with REST API
- **static/index.html** - Web UI HTML
- **static/style.css** - Web UI styles
- **static/app.js** - Web UI JavaScript

## Tests (`tests/`)

- **conftest.py** - Pytest configuration and fixtures
- **test_cli.py** - CLI tests
- **test_converters.py** - Converter tests
- **test_normalizer.py** - Normalizer tests
- **test_web.py** - Web UI API tests

## CI/CD (`.github/workflows/`)

- **ci.yml** - GitHub Actions workflow for testing and linting

## Design Principles

1. **Clean Structure** - Logical organization by functionality
2. **Minimal Documentation** - Essential docs only (README, QUICK_START, CHANGELOG)
3. **Production Ready** - Full error handling, logging, and type hints
4. **Testable** - Comprehensive test coverage
5. **Extensible** - Plugin architecture for new converters

## Key Features

- ✅ CLI and Web UI interfaces
- ✅ Multiple format support (DOCX, PDF, XLSX)
- ✅ MkDocs-ready output
- ✅ Quality scoring and reporting
- ✅ Image extraction and management
- ✅ Link rewriting
- ✅ OCR support for scanned PDFs
- ✅ Cross-platform compatibility

## Dependencies

### Core
- typer, rich - CLI framework
- pyyaml - YAML processing
- mammoth - DOCX conversion (fallback)
- pymupdf - PDF processing
- openpyxl - Excel processing
- Pillow - Image processing

### Web UI
- fastapi - Web framework
- uvicorn - ASGI server
- python-multipart - File upload handling

### Optional
- pandoc - Better DOCX conversion (external)
- tesseract - OCR for scanned PDFs (external)

### Development
- pytest - Testing framework
- black - Code formatting
- ruff - Linting
- mypy - Type checking

## Getting Started

See [QUICK_START.md](../QUICK_START.md) for installation and usage instructions.

