# Architecture

This document describes the architecture and design of doc2mkdocs.

## Overview

doc2mkdocs is built on a plugin-based architecture that separates concerns into distinct layers:

1. **CLI Layer** - User interface and command handling
2. **Converter Layer** - Format-specific document conversion
3. **Normalization Layer** - Markdown processing and standardization
4. **Utility Layer** - Shared utilities and helpers
5. **Reporting Layer** - Conversion tracking and reporting

## Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      CLI (cli.py)                       │
│  - Command parsing                                      │
│  - File collection                                      │
│  - Orchestration                                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──────────────────────────────────────┐
                 │                                      │
┌────────────────▼──────────┐          ┌───────────────▼──────────┐
│   Converter Layer         │          │  Normalization Layer     │
│  ┌──────────────────────┐ │          │  ┌────────────────────┐  │
│  │  BaseConverter       │ │          │  │ MarkdownNormalizer │  │
│  │  (interface)         │ │          │  │ - Heading fixes    │  │
│  └──────────────────────┘ │          │  │ - Whitespace       │  │
│           ▲                │          │  │ - Front matter     │  │
│           │                │          │  └────────────────────┘  │
│  ┌────────┴────────┐       │          │  ┌────────────────────┐  │
│  │                 │       │          │  │  LinkRewriter      │  │
│  │  DocxConverter  │       │          │  │ - Internal links   │  │
│  │  PdfConverter   │       │          │  │ - Anchor normalization│
│  │  XlsxConverter  │       │          │  └────────────────────┘  │
│  │                 │       │          │  ┌────────────────────┐  │
│  └─────────────────┘       │          │  │  ImageHandler      │  │
│                            │          │  │ - Extract images   │  │
└────────────────────────────┘          │  │ - Rewrite paths    │  │
                                        │  └────────────────────┘  │
                                        └─────────────────────────┘
                 │
                 │
┌────────────────▼──────────────────────────────────────┐
│                  Reporting Layer                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │  ConversionReport                                │ │
│  │  - Track conversions                             │ │
│  │  - Quality scores                                │ │
│  │  - JSON/text output                              │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

## Core Concepts

### Plugin Architecture

All converters implement the `BaseConverter` interface:

```python
class BaseConverter(ABC):
    @abstractmethod
    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the file."""
        
    @abstractmethod
    def convert(self, file_path: Path) -> ConversionResult:
        """Convert document to Markdown."""
        
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Get supported file extensions."""
```

This allows easy addition of new converters without modifying existing code.

### Conversion Pipeline

Each file goes through a standardized pipeline:

1. **Detection** - Identify file type and select converter
2. **Conversion** - Extract content using format-specific logic
3. **Normalization** - Apply standard transformations:
   - Heading normalization
   - Whitespace cleanup
   - Image extraction and path rewriting
   - Link rewriting
   - Front matter addition
4. **Writing** - Save to disk with proper structure
5. **Reporting** - Track results and quality

### Quality Scoring

Each conversion receives a quality score (0.0-1.0) based on:

- **Base score**: 1.0
- **Warnings**: -0.05 per warning
- **Errors**: -0.2 per error
- **Special cases**:
  - Scanned PDF without OCR: 0.3
  - Scanned PDF with OCR: 0.6

### Configuration

The `ConversionConfig` dataclass holds all configuration:

- Input/output paths
- Conversion options (OCR mode, Excel mode, etc.)
- Feature flags (front matter, nav generation)
- Internal state (converted files mapping)

## Key Design Decisions

### Why Typer for CLI?

- Type-safe command definitions
- Automatic help generation
- Rich integration for beautiful output
- Better than argparse for complex CLIs

### Why Plugin Architecture?

- Easy to add new converters
- Separation of concerns
- Testable in isolation
- Users can add custom converters

### Why Separate Normalization?

- Shared logic across all converters
- Consistent output quality
- Easier to maintain and test
- MkDocs-specific transformations in one place

### Why Quality Scores?

- Help users identify problematic conversions
- Prioritize manual review
- Track conversion reliability
- Useful for batch processing

## File Organization

```
src/doc2mkdocs/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for python -m
├── cli.py                # CLI implementation
├── core/                 # Core abstractions
│   ├── base_converter.py # Converter interface
│   ├── config.py         # Configuration
│   └── report.py         # Reporting
├── converters/           # Format-specific converters
│   ├── docx_converter.py
│   ├── pdf_converter.py
│   └── xlsx_converter.py
├── normalizer/           # Markdown processing
│   ├── markdown_normalizer.py
│   ├── link_rewriter.py
│   └── image_handler.py
└── utils/                # Shared utilities
    ├── filename_sanitizer.py
    └── logger.py
```

## Extension Points

### Adding a New Converter

1. Create new file in `converters/`
2. Implement `BaseConverter` interface
3. Register in `converters/__init__.py`
4. Add to CLI converter list
5. Write tests

### Adding a New Normalization Step

1. Add method to `MarkdownNormalizer`
2. Call from CLI pipeline
3. Add tests

### Adding a New CLI Option

1. Add parameter to `convert()` command
2. Add to `ConversionConfig`
3. Use in relevant converter/normalizer
4. Update documentation

## Testing Strategy

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test converter + normalizer pipeline
- **CLI tests**: Test command-line interface
- **Fixtures**: Shared test data and configurations

## Performance Considerations

- **Lazy loading**: Converters only loaded when needed
- **Streaming**: Large files processed in chunks where possible
- **Parallel processing**: Future enhancement for batch conversion
- **Memory limits**: Excel converter limits table size

## Security Considerations

- **Path traversal**: All paths validated and sanitized
- **File size limits**: Excel converter limits table dimensions
- **Safe filename generation**: Special characters removed
- **No code execution**: Pure data processing, no eval/exec

## Future Enhancements

- Parallel file processing
- Watch mode for automatic conversion
- Web UI for upload/download
- Custom converter plugins via entry points
- Incremental conversion (only changed files)
- Better table detection in PDFs
- PPTX, HTML, TXT support

