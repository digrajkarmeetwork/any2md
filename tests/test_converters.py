"""Tests for document converters."""

from pathlib import Path

import pytest

from doc2mkdocs.converters import DocxConverter, PdfConverter, XlsxConverter


class TestDocxConverter:
    """Tests for DOCX converter."""

    def test_can_convert_docx(self, sample_config):
        """Test that converter recognizes DOCX files."""
        converter = DocxConverter(sample_config)

        assert converter.can_convert(Path("test.docx"))
        assert converter.can_convert(Path("test.doc"))
        assert not converter.can_convert(Path("test.pdf"))

    def test_supported_extensions(self, sample_config):
        """Test supported extensions."""
        converter = DocxConverter(sample_config)

        assert ".docx" in converter.supported_extensions
        assert ".doc" in converter.supported_extensions


class TestPdfConverter:
    """Tests for PDF converter."""

    def test_can_convert_pdf(self, sample_config):
        """Test that converter recognizes PDF files."""
        converter = PdfConverter(sample_config)

        assert converter.can_convert(Path("test.pdf"))
        assert not converter.can_convert(Path("test.docx"))

    def test_supported_extensions(self, sample_config):
        """Test supported extensions."""
        converter = PdfConverter(sample_config)

        assert ".pdf" in converter.supported_extensions


class TestXlsxConverter:
    """Tests for XLSX converter."""

    def test_can_convert_xlsx(self, sample_config):
        """Test that converter recognizes XLSX files."""
        converter = XlsxConverter(sample_config)

        assert converter.can_convert(Path("test.xlsx"))
        assert converter.can_convert(Path("test.xls"))
        assert not converter.can_convert(Path("test.pdf"))

    def test_supported_extensions(self, sample_config):
        """Test supported extensions."""
        converter = XlsxConverter(sample_config)

        assert ".xlsx" in converter.supported_extensions
        assert ".xls" in converter.supported_extensions

