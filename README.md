# doc2mkdocs

Convert documentation files (DOCX, PDF, XLSX) into high-quality, MkDocs-ready Markdown with a single command.

## Features

- **One Command**: Convert entire directories of documents with `doc2mkdocs convert`
- **Multiple Formats**: Support for DOCX, PDF, and Excel (XLSX) files
- **MkDocs-Ready**: Outputs properly structured Markdown with sanitized filenames and relative links
- **Smart Asset Management**: Automatically extracts and organizes images
- **Quality Reports**: Generates detailed conversion reports with quality scores
- **OCR Support**: Optional OCR for scanned PDFs using Tesseract
- **Link Rewriting**: Automatically rewrites internal document links to work in MkDocs
- **Front Matter**: Optional YAML front matter for metadata
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Standard Installation

```bash
pip install .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### With Optional Features

```bash
# Web UI support
pip install ".[web]"

# Watch mode support
pip install ".[watch]"

# All features
pip install ".[dev,web,watch]"
```

### Prerequisites

For PDF OCR support, install Tesseract:

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

For best DOCX conversion, install Pandoc (optional):

**Windows:**
```bash
choco install pandoc
```

**macOS:**
```bash
brew install pandoc
```

**Linux:**
```bash
sudo apt-get install pandoc
```

## Quick Start

### CLI: Convert a Single File

```bash
doc2mkdocs convert my-document.docx --out docs/
```

### CLI: Convert a Directory (Recursive)

```bash
doc2mkdocs convert ./source-docs --out docs/
```

### CLI: With Custom Options

```bash
doc2mkdocs convert ./source-docs \
  --out docs/ \
  --assets-dir docs/images \
  --excel-mode single-page \
  --pdf-ocr auto \
  --mkdocs-nav \
  --overwrite
```

### Web UI: Drag & Drop Interface

```bash
# Install with web dependencies
pip install .[web]

# Start the web server
doc2mkdocs serve

# Open browser to http://127.0.0.1:8000
# Drag and drop files to convert and download as ZIP
```

**Web UI Features:**
- 🖱️ Drag-and-drop file upload
- ✅ Real-time file validation
- 📊 Live conversion progress
- 📈 Quality scores and warnings
- 📦 Download results as ZIP
- 🎨 Clean, responsive interface

## Usage

### Command-Line Interface

#### Convert Command

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

#### Serve Command (Web UI)

```
doc2mkdocs serve [OPTIONS]
```

**Options:**
- `--host TEXT`: Host to bind to (default: `127.0.0.1`)
- `--port INTEGER`: Port to bind to (default: `8000`)
- `--reload`: Enable auto-reload for development

**Example:**
```bash
# Start on default port
doc2mkdocs serve

# Start on custom port
doc2mkdocs serve --port 3000

# Allow external connections
doc2mkdocs serve --host 0.0.0.0 --port 8080
```

### Web Interface

The web UI provides a user-friendly interface for converting documents:

1. **Upload**: Drag and drop files or click to browse
2. **Validation**: Files are validated before conversion
3. **Processing**: Real-time progress updates
4. **Results**: View quality scores, warnings, and errors
5. **Download**: Get all converted files as a ZIP

**Supported in Web UI:**
- Multiple file upload
- File size limit: 50MB per file
- All conversion options (OCR, Excel modes, etc.)
- Detailed conversion reports
- Automatic cleanup of temporary files

### Example Output Structure

```
docs/
├── assets/
│   ├── user-guide/
│   │   ├── image-001.png
│   │   └── image-002.png
│   └── api-reference/
│       └── diagram-001.png
├── user-guide.md
├── api-reference.md
├── conversion-report.json
└── mkdocs-nav-snippet.yml
```

## Demo Example

### Input

```
source-docs/
├── User Guide.docx
├── API Reference.pdf
└── Data Tables.xlsx
```

### Command

```bash
doc2mkdocs convert source-docs/ --out docs/ --mkdocs-nav
```

### Output

```
docs/
├── assets/
│   ├── user-guide/
│   │   ├── screenshot-001.png
│   │   └── diagram-001.png
│   ├── api-reference/
│   │   └── architecture-001.png
│   └── data-tables/
│       └── chart-001.png
├── user-guide.md
├── api-reference.md
├── data-tables.md
├── conversion-report.json
└── mkdocs-nav-snippet.yml
```

### Sample Output File (user-guide.md)

```markdown
---
title: User Guide
source: source-docs/User Guide.docx
converted_at: 2025-12-15T10:30:00
---

# User Guide

## Getting Started

Welcome to our application! This guide will help you get started.

![Screenshot](assets/user-guide/screenshot-001.png)

## Features

- Easy to use interface
- Powerful automation
- Cross-platform support

For more details, see the [API Reference](api-reference.md).
```

### Sample Conversion Report

```json
{
  "start_time": "2025-12-15T10:30:00",
  "end_time": "2025-12-15T10:30:05",
  "total_files": 3,
  "successful": 3,
  "failed": 0,
  "average_quality_score": 0.95,
  "files": [
    {
      "source_file": "source-docs/User Guide.docx",
      "output_file": "docs/user-guide.md",
      "success": true,
      "warnings": [],
      "errors": [],
      "quality_score": 1.0,
      "converter_used": "DocxConverter",
      "conversion_time_ms": 1250
    }
  ]
}
```

## How It Works

doc2mkdocs uses a four-stage pipeline:

1. **Detect**: Identifies file types and selects appropriate converter
2. **Convert**: Extracts content using format-specific converters
   - DOCX: Pandoc (if available) or Mammoth
   - PDF: PyMuPDF for text/images, optional Tesseract OCR
   - XLSX: openpyxl with Markdown table generation
3. **Normalize**: Processes markdown for MkDocs compatibility
   - Heading normalization (single H1, no level jumps)
   - Image extraction and path rewriting
   - Link rewriting for internal references
   - Whitespace normalization
4. **Write**: Outputs markdown files with optional front matter
5. **Report**: Generates conversion report with quality scores

## Conversion Quality

Each converted file receives a quality score (0.0-1.0) based on:

- Successful extraction of content
- Number of warnings/errors encountered
- Detection of scanned vs. text-based PDFs
- Table complexity in Excel files

Quality scores help identify files that may need manual review.

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/doc2mkdocs --cov-report=html
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/doc2mkdocs.git
cd doc2mkdocs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Building Standalone Executable

You can build a standalone executable using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_executable.py
```

The executable will be created in the `dist/` directory and can be distributed without requiring Python installation.

**Note**: Users will still need Tesseract and Pandoc installed for full functionality (OCR and best DOCX conversion).

### Platform-Specific Builds

**Windows:**
```bash
python build_executable.py
# Creates: dist/doc2mkdocs.exe
```

**macOS/Linux:**
```bash
python build_executable.py
# Creates: dist/doc2mkdocs
```

## Troubleshooting

### Common Issues

**"Pandoc not found" warning**
- Install Pandoc for best DOCX conversion quality
- The tool will fall back to Mammoth (pure Python) if Pandoc is unavailable

**"Tesseract not found" error with OCR**
- Install Tesseract OCR for scanned PDF support
- Use `--pdf-ocr off` to disable OCR if not needed

**"Permission denied" on output directory**
- Ensure you have write permissions to the output directory
- Try using `--out` to specify a different output location

**Large Excel files cause memory issues**
- The tool automatically limits table size to 1000x50 cells
- Consider splitting large Excel files before conversion

**Links not working in MkDocs**
- Ensure all referenced documents are converted in the same run
- Check the conversion report for unresolved links

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Web UI Guide](WEB_UI_GUIDE.md)** - Complete guide to the web interface
- **[Architecture](ARCHITECTURE.md)** - Technical architecture and design
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines
- **[Changelog](CHANGELOG.md)** - Version history

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

