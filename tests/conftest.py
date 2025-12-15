"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from doc2mkdocs.core.config import ConversionConfig, ExcelMode, PDFOCRMode


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config(temp_dir):
    """Create a sample conversion configuration."""
    input_path = temp_dir / "input"
    output_dir = temp_dir / "output"
    input_path.mkdir()
    output_dir.mkdir()

    return ConversionConfig(
        input_path=input_path,
        output_dir=output_dir,
        excel_mode=ExcelMode.SHEET_PER_PAGE,
        pdf_ocr=PDFOCRMode.AUTO,
        overwrite=False,
        front_matter=True,
        mkdocs_nav=False,
        log_level="info",
    )


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Main Title

## Section 1

This is some content.

### Subsection 1.1

More content here.

## Section 2

Final section.
"""

