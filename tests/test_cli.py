"""Tests for CLI functionality."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from doc2mkdocs.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_convert_help(self):
        """Test that help command works."""
        result = runner.invoke(app, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Convert documentation files" in result.stdout

    def test_convert_nonexistent_file(self):
        """Test converting a nonexistent file."""
        result = runner.invoke(app, ["convert", "nonexistent.docx"])
        # Should handle gracefully
        assert "No convertible files found" in result.stdout or result.exit_code != 0

    def test_app_version(self):
        """Test that app can be invoked."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "doc2mkdocs" in result.stdout.lower()

