"""Filename sanitization utilities."""

import re
from pathlib import Path


def sanitize_filename(filename: str, lowercase: bool = True) -> str:
    """Sanitize a filename for use in URLs and file systems.

    Args:
        filename: Original filename
        lowercase: Whether to convert to lowercase

    Returns:
        Sanitized filename
    """
    # Remove extension for processing
    path = Path(filename)
    name = path.stem
    ext = path.suffix

    # Replace spaces with dashes
    name = name.replace(" ", "-")

    # Replace underscores with dashes for consistency
    name = name.replace("_", "-")

    # Remove or replace unsafe characters
    # Keep only alphanumeric, dashes, and dots
    name = re.sub(r"[^a-zA-Z0-9\-.]", "", name)

    # Remove multiple consecutive dashes
    name = re.sub(r"-+", "-", name)

    # Remove leading/trailing dashes
    name = name.strip("-")

    # Convert to lowercase if requested
    if lowercase:
        name = name.lower()

    # Ensure we have a valid name
    if not name:
        name = "unnamed"

    return name + ext


def get_unique_filename(base_path: Path, desired_name: str) -> Path:
    """Get a unique filename by appending numbers if necessary.

    Args:
        base_path: Base directory path
        desired_name: Desired filename

    Returns:
        Unique file path
    """
    path = base_path / desired_name
    if not path.exists():
        return path

    # File exists, append numbers
    name_path = Path(desired_name)
    stem = name_path.stem
    suffix = name_path.suffix

    counter = 2
    while True:
        new_name = f"{stem}-{counter}{suffix}"
        path = base_path / new_name
        if not path.exists():
            return path
        counter += 1

