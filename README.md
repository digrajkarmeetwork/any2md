# doc2mkdocs

Convert documentation files (DOCX, PDF, XLSX) into MkDocs-ready Markdown with a single command or web interface.

## Features

- 🚀 **CLI & Web UI**: Command-line tool or drag-and-drop web interface
- 📄 **Multiple Formats**: DOCX, PDF, and Excel (XLSX) support
- 🖼️ **Smart Assets**: Automatic image extraction and organization
- 📊 **Quality Reports**: Detailed conversion reports with quality scores
- 🔗 **Link Rewriting**: Automatic internal link conversion for MkDocs
- 🎯 **MkDocs-Ready**: Proper structure, sanitized filenames, YAML front matter
- 🔍 **OCR Support**: Optional OCR for scanned PDFs (Tesseract)
- 🌐 **Cross-Platform**: Windows, macOS, and Linux

## Quick Start

### Installation

```bash
# Basic installation
pip install .

# With web UI
pip install ".[web]"

# Development mode
pip install -e ".[dev,web]"
```

### CLI Usage

```bash
# Convert a single file
doc2mkdocs convert document.docx --out docs/

# Convert a directory
doc2mkdocs convert ./source-docs --out docs/ --mkdocs-nav

# With custom options
doc2mkdocs convert ./source-docs --out docs/ --pdf-ocr auto --overwrite
```

### Web UI

```bash
# Start the web server
doc2mkdocs serve

# Or use the startup script
python start_web_ui.py
```

Then open **http://127.0.0.1:8000** in your browser and drag-and-drop files to convert.

## CLI Reference

### Convert Command

```
doc2mkdocs convert <input_path> [OPTIONS]
```

**Arguments:**
- `input_path`: File or directory to convert (required)

**Options:**
- `--out PATH`: Output directory (default: `docs`)
- `--assets-dir PATH`: Assets directory (default: `<out>/assets`)
- `--split-by-heading`: Split long documents by heading
- `--excel-mode [sheet-per-page|single-page]`: Excel conversion mode (default: `sheet-per-page`)
- `--pdf-ocr [off|auto|on]`: PDF OCR mode (default: `auto`)
- `--overwrite`: Overwrite existing files
- `--front-matter/--no-front-matter`: Add YAML front matter (default: enabled)
- `--mkdocs-nav`: Generate mkdocs.yml nav snippet
- `--report PATH`: Report output path (default: `<out>/conversion-report.json`)
- `--log-level [debug|info|warning|error]`: Log level (default: `info`)

### Serve Command

```bash
doc2mkdocs serve [--host HOST] [--port PORT] [--reload]
```

**Options:**
- `--host`: Host to bind to (default: `127.0.0.1`)
- `--port`: Port to bind to (default: `8000`)
- `--reload`: Enable auto-reload for development

## Output Structure

```
docs/
├── assets/
│   ├── document-name/
│   │   ├── image-001.png
│   │   └── image-002.png
├── document-name.md
├── conversion-report.json
└── mkdocs-nav-snippet.yml  # if --mkdocs-nav used
```

## Optional Dependencies

### Tesseract OCR (for scanned PDFs)

**Windows:** Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
**macOS:** `brew install tesseract`
**Linux:** `sudo apt-get install tesseract-ocr`

### Pandoc (for better DOCX conversion)

**Windows:** `choco install pandoc`
**macOS:** `brew install pandoc`
**Linux:** `sudo apt-get install pandoc`

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format and lint
black src/ tests/
ruff check src/ tests/
mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! See [CHANGELOG.md](CHANGELOG.md) for version history.

