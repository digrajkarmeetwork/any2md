"""DOCX to Markdown converter."""

import io
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import mammoth

from doc2mkdocs.core.base_converter import BaseConverter, ConversionResult
from doc2mkdocs.core.config import ConversionConfig

logger = logging.getLogger(__name__)


class DocxConverter(BaseConverter):
    """Convert DOCX files to Markdown."""

    def __init__(self, config: ConversionConfig):
        """Initialize DOCX converter.

        Args:
            config: Conversion configuration
        """
        super().__init__(config)
        self.pandoc_available = self._check_pandoc()

    def _check_pandoc(self) -> bool:
        """Check if pandoc is available.

        Returns:
            True if pandoc is available
        """
        return shutil.which("pandoc") is not None

    @property
    def supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions
        """
        return [".docx", ".doc"]

    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the file.

        Args:
            file_path: Path to file

        Returns:
            True if file can be converted
        """
        return file_path.suffix.lower() in self.supported_extensions

    def convert(self, file_path: Path) -> ConversionResult:
        """Convert DOCX to Markdown.

        Args:
            file_path: Path to DOCX file

        Returns:
            Conversion result
        """
        result = ConversionResult(success=True)

        try:
            # Try pandoc first if available
            if self.pandoc_available:
                logger.debug(f"Converting {file_path} using pandoc")
                markdown, images = self._convert_with_pandoc(file_path)
                result.markdown_content = markdown
                result.images = images
            else:
                # Fallback to mammoth
                logger.debug(f"Converting {file_path} using mammoth")
                markdown, images = self._convert_with_mammoth(file_path)
                result.markdown_content = markdown
                result.images = images
                result.add_warning("Pandoc not available, using mammoth (may have reduced quality)")

            # Extract metadata
            result.metadata["title"] = file_path.stem.replace("-", " ").title()

            # Quality heuristics
            if len(result.markdown_content.strip()) < 100:
                result.add_warning("Document appears to be very short or mostly empty")

        except Exception as e:
            logger.error(f"Failed to convert {file_path}: {e}")
            result.add_error(f"Conversion failed: {str(e)}")

        return result

    def _convert_with_pandoc(self, file_path: Path) -> tuple[str, dict[str, bytes]]:
        """Convert using pandoc.

        Args:
            file_path: Path to DOCX file

        Returns:
            Tuple of (markdown content, images dict)
        """
        try:
            # Run pandoc
            result = subprocess.run(
                [
                    "pandoc",
                    str(file_path),
                    "-f", "docx",
                    "-t", "markdown",
                    "--extract-media", ".",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            markdown = result.stdout

            # TODO: Extract images from media folder
            # For now, return empty images dict
            images: dict[str, bytes] = {}

            return markdown, images

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")

    def _convert_with_mammoth(self, file_path: Path) -> tuple[str, dict[str, bytes]]:
        """Convert using mammoth.

        Args:
            file_path: Path to DOCX file

        Returns:
            Tuple of (markdown content, images dict)
        """
        images: dict[str, bytes] = {}

        def image_converter(image: mammoth.images.Image) -> dict[str, str]:
            """Convert images during mammoth processing."""
            # Read image bytes
            with image.open() as image_bytes:
                content = image_bytes.read()

            # Generate image filename
            extension = image.content_type.split("/")[-1]
            if extension == "jpeg":
                extension = "jpg"
            image_name = f"image-{len(images) + 1:03d}.{extension}"

            # Store image
            images[image_name] = content

            # Return markdown image reference
            return {"src": image_name}

        # Convert with mammoth
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(
                docx_file,
                convert_image=mammoth.images.img_element(image_converter),
            )

        markdown = result.value

        # Log any messages from mammoth
        for message in result.messages:
            logger.debug(f"Mammoth: {message}")

        return markdown, images

