# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-16

### Added

- **Web UI**: Complete web-based interface for document conversion
  - Drag-and-drop file upload
  - Real-time file validation
  - Live conversion progress tracking
  - Quality scores and detailed reports
  - Download results as ZIP
  - Responsive design for desktop and tablet
- **New CLI command**: `doc2mkdocs serve` to launch web UI
- **REST API**: Full API for programmatic access
  - `/api/validate` - Validate files before upload
  - `/api/upload` - Upload and convert files
  - `/api/status/{job_id}` - Check conversion status
  - `/api/download/{job_id}` - Download results
  - `/api/job/{job_id}` - Delete conversion job
- **Web UI Guide**: Comprehensive documentation for web interface
- **Tests**: Full test suite for web endpoints

### Changed

- Updated README with web UI usage examples
- Enhanced installation instructions for web dependencies

## [1.0.0] - 2025-12-15

### Added

- Initial release of doc2mkdocs
- DOCX to Markdown conversion using Pandoc or Mammoth
- PDF to Markdown conversion using PyMuPDF
- XLSX to Markdown conversion using openpyxl
- Optional OCR support for scanned PDFs using Tesseract
- Automatic image extraction and organization
- Link rewriting for MkDocs compatibility
- Heading normalization (single H1, no level jumps)
- YAML front matter generation
- Filename sanitization (spaces to dashes, lowercase, safe chars)
- Conversion quality scoring
- JSON and human-readable conversion reports
- MkDocs navigation snippet generation
- Recursive directory conversion
- Duplicate filename handling
- CLI with comprehensive options
- Cross-platform support (Windows, macOS, Linux)
- Comprehensive test suite
- Type hints throughout
- Linting configuration (Black, Ruff, MyPy)
- GitHub Actions CI workflow

### Converter Features

#### DOCX Converter
- Preserves headings, lists, links, and tables
- Image extraction
- Pandoc integration for best quality
- Mammoth fallback for pure Python conversion

#### PDF Converter
- Text extraction from text-based PDFs
- Scanned PDF detection
- Optional OCR with quality warnings
- Image extraction
- Metadata extraction (title, author)

#### XLSX Converter
- Sheet-per-page or single-page modes
- Markdown table generation
- HTML table fallback for complex formatting
- Large sheet handling with warnings
- Multi-sheet support

### Normalization Features
- Heading structure normalization
- Image path rewriting
- Internal link rewriting
- Anchor normalization
- Whitespace normalization
- Front matter generation

## [Unreleased]

### Planned Features
- PPTX support
- HTML support
- TXT support
- Watch mode for automatic conversion
- Web UI for file upload and conversion
- Split by heading for long documents
- Custom converter plugins
- Batch processing optimizations
- Progress bars for large conversions
- PyInstaller executable builds

