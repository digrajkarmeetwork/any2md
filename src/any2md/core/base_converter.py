"""Base converter interface for all document converters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from doc2mkdocs.core.config import ConversionConfig


@dataclass
class ConversionResult:
    """Result of a document conversion."""

    success: bool
    markdown_content: str = ""
    images: dict[str, bytes] = field(default_factory=dict)
    """Maps image filename to image bytes."""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    quality_score: float = 1.0
    """Quality/confidence score from 0.0 to 1.0."""
    metadata: dict[str, str] = field(default_factory=dict)
    """Document metadata for front matter."""

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        # Reduce quality score slightly for warnings
        self.quality_score = max(0.0, self.quality_score - 0.05)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.success = False
        # Reduce quality score significantly for errors
        self.quality_score = max(0.0, self.quality_score - 0.2)


class BaseConverter(ABC):
    """Base class for all document converters."""

    def __init__(self, config: ConversionConfig):
        """Initialize converter with configuration.

        Args:
            config: Conversion configuration
        """
        self.config = config

    @abstractmethod
    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this converter can handle the file
        """
        pass

    @abstractmethod
    def convert(self, file_path: Path) -> ConversionResult:
        """Convert a document to Markdown.

        Args:
            file_path: Path to the file to convert

        Returns:
            ConversionResult with markdown content and metadata
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            List of extensions (e.g., ['.docx', '.doc'])
        """
        pass

