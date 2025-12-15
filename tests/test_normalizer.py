"""Tests for normalizer components."""

import pytest

from doc2mkdocs.normalizer import MarkdownNormalizer
from doc2mkdocs.utils import sanitize_filename


class TestMarkdownNormalizer:
    """Tests for MarkdownNormalizer."""

    def test_normalize_headings_multiple_h1(self):
        """Test that multiple H1 headings are converted to H2."""
        content = """# First Title

Some content.

# Second Title

More content.
"""
        normalizer = MarkdownNormalizer()
        normalized, warnings = normalizer.normalize_headings(content)

        assert "# First Title" in normalized
        assert "## Second Title" in normalized
        assert len(warnings) == 1
        assert "Multiple H1" in warnings[0]

    def test_normalize_headings_level_jump(self):
        """Test that heading level jumps are fixed."""
        content = """# Title

#### Subsection
"""
        normalizer = MarkdownNormalizer()
        normalized, warnings = normalizer.normalize_headings(content)

        assert "## Subsection" in normalized
        assert len(warnings) == 1
        assert "jump" in warnings[0].lower()

    def test_add_front_matter(self):
        """Test adding YAML front matter."""
        content = "# Title\n\nContent"
        normalizer = MarkdownNormalizer()

        result = normalizer.add_front_matter(
            content,
            title="Test Document",
            source="test.docx",
            converted_at="2025-01-01T00:00:00",
        )

        assert result.startswith("---\n")
        assert "title: Test Document" in result
        assert "source: test.docx" in result
        assert "converted_at: 2025-01-01T00:00:00" in result
        assert "---\n" in result
        assert "# Title" in result

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        content = "Line 1  \n\n\n\n\nLine 2\n\n\nLine 3"
        normalizer = MarkdownNormalizer()

        result = normalizer.normalize_whitespace(content)

        # Should reduce multiple blank lines
        assert "\n\n\n\n" not in result
        # Should end with single newline
        assert result.endswith("\n")
        assert not result.endswith("\n\n")


class TestFilenameSanitizer:
    """Tests for filename sanitization."""

    def test_sanitize_filename_spaces(self):
        """Test that spaces are replaced with dashes."""
        assert sanitize_filename("My Document.docx") == "my-document.docx"

    def test_sanitize_filename_special_chars(self):
        """Test that special characters are removed."""
        assert sanitize_filename("Doc@#$%ument!.pdf") == "document.pdf"

    def test_sanitize_filename_multiple_dashes(self):
        """Test that multiple dashes are collapsed."""
        assert sanitize_filename("my---document.txt") == "my-document.txt"

    def test_sanitize_filename_underscores(self):
        """Test that underscores are converted to dashes."""
        assert sanitize_filename("my_document.md") == "my-document.md"

    def test_sanitize_filename_empty(self):
        """Test that empty names get a default."""
        assert sanitize_filename("@#$.txt") == "unnamed.txt"

    def test_sanitize_filename_no_lowercase(self):
        """Test sanitization without lowercasing."""
        assert sanitize_filename("MyDocument.pdf", lowercase=False) == "MyDocument.pdf"

