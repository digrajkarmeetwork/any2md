"""Image extraction and handling."""

import re
from pathlib import Path
from typing import Optional

from doc2mkdocs.core.config import ConversionConfig
from doc2mkdocs.utils.filename_sanitizer import get_unique_filename, sanitize_filename


class ImageHandler:
    """Handle image extraction and path rewriting."""

    def __init__(self, config: ConversionConfig, document_name: str):
        """Initialize image handler.

        Args:
            config: Conversion configuration
            document_name: Name of the document (for organizing images)
        """
        self.config = config
        self.document_name = sanitize_filename(Path(document_name).stem)
        self.image_dir = config.assets_dir / self.document_name
        self.image_counter = 0

    def save_images(
        self, images: dict[str, bytes], markdown_file: Path
    ) -> dict[str, str]:
        """Save images to disk and return mapping of old names to new paths.

        Args:
            images: Dictionary mapping image names to image bytes
            markdown_file: Path to the markdown file (for relative path calculation)

        Returns:
            Dictionary mapping original image names to new relative paths
        """
        if not images:
            return {}

        # Create image directory
        self.image_dir.mkdir(parents=True, exist_ok=True)

        image_mapping = {}

        for original_name, image_bytes in images.items():
            # Sanitize image filename
            sanitized_name = sanitize_filename(original_name)

            # Ensure unique filename
            image_path = get_unique_filename(self.image_dir, sanitized_name)

            # Write image
            image_path.write_bytes(image_bytes)

            # Calculate relative path from markdown file to image
            try:
                rel_path = image_path.relative_to(markdown_file.parent)
                image_mapping[original_name] = str(rel_path).replace("\\", "/")
            except ValueError:
                # Fallback to absolute path from docs root
                try:
                    rel_path = image_path.relative_to(self.config.output_dir)
                    image_mapping[original_name] = "/" + str(rel_path).replace("\\", "/")
                except ValueError:
                    # Last resort: use the full path
                    image_mapping[original_name] = str(image_path).replace("\\", "/")

        return image_mapping

    def rewrite_image_paths(self, content: str, image_mapping: dict[str, str]) -> str:
        """Rewrite image paths in markdown content.

        Args:
            content: Markdown content
            image_mapping: Mapping of original image names to new paths

        Returns:
            Content with rewritten image paths
        """
        if not image_mapping:
            return content

        def replace_image(match: re.Match[str]) -> str:
            alt_text = match.group(1)
            image_path = match.group(2)

            # Extract just the filename from the path
            image_name = Path(image_path).name

            # Look up new path
            new_path = image_mapping.get(image_name, image_mapping.get(image_path, image_path))

            return f"![{alt_text}]({new_path})"

        # Replace markdown image syntax: ![alt](path)
        content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, content)

        return content

    def generate_image_name(self, extension: str = ".png") -> str:
        """Generate a unique image name.

        Args:
            extension: Image file extension

        Returns:
            Generated image filename
        """
        self.image_counter += 1
        return f"image-{self.image_counter:03d}{extension}"

