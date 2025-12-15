"""Markdown normalization utilities."""

import re
from typing import Optional


class MarkdownNormalizer:
    """Normalize markdown content for MkDocs."""

    @staticmethod
    def normalize_headings(content: str) -> tuple[str, list[str]]:
        """Normalize heading structure.

        Ensures:
        - Only one H1 heading
        - No heading level jumps (e.g., H1 -> H3)
        - Proper heading hierarchy

        Args:
            content: Markdown content

        Returns:
            Tuple of (normalized content, list of warnings)
        """
        warnings = []
        lines = content.split("\n")
        normalized_lines = []
        h1_count = 0
        last_level = 0

        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)

                # Handle multiple H1s
                if level == 1:
                    h1_count += 1
                    if h1_count > 1:
                        # Convert additional H1s to H2s
                        line = f"## {title}"
                        warnings.append(f"Multiple H1 headings found, converted '{title}' to H2")
                        level = 2

                # Check for heading jumps
                if last_level > 0 and level > last_level + 1:
                    # Reduce jump
                    new_level = last_level + 1
                    line = "#" * new_level + f" {title}"
                    warnings.append(
                        f"Heading level jump detected (H{last_level} -> H{level}), "
                        f"adjusted '{title}' to H{new_level}"
                    )
                    level = new_level

                last_level = level

            normalized_lines.append(line)

        return "\n".join(normalized_lines), warnings

    @staticmethod
    def add_front_matter(
        content: str, title: str, source: str, converted_at: str, **extra: str
    ) -> str:
        """Add YAML front matter to markdown content.

        Args:
            content: Markdown content
            title: Document title
            source: Source file path
            converted_at: Conversion timestamp
            **extra: Additional metadata fields

        Returns:
            Content with front matter
        """
        front_matter_lines = [
            "---",
            f"title: {title}",
            f"source: {source}",
            f"converted_at: {converted_at}",
        ]

        for key, value in extra.items():
            front_matter_lines.append(f"{key}: {value}")

        front_matter_lines.append("---")
        front_matter_lines.append("")

        return "\n".join(front_matter_lines) + content

    @staticmethod
    def normalize_whitespace(content: str) -> str:
        """Normalize whitespace in markdown content.

        Args:
            content: Markdown content

        Returns:
            Content with normalized whitespace
        """
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in content.split("\n")]

        # Remove multiple consecutive blank lines
        normalized_lines = []
        blank_count = 0

        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:  # Allow max 2 consecutive blank lines
                    normalized_lines.append(line)
            else:
                blank_count = 0
                normalized_lines.append(line)

        # Ensure file ends with single newline
        content = "\n".join(normalized_lines)
        return content.rstrip() + "\n"

