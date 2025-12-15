"""Link rewriting for MkDocs compatibility."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote, unquote, urlparse

from doc2mkdocs.core.config import ConversionConfig


class LinkRewriter:
    """Rewrite links for MkDocs compatibility."""

    def __init__(self, config: ConversionConfig, current_file: Path):
        """Initialize link rewriter.

        Args:
            config: Conversion configuration
            current_file: Current markdown file being processed
        """
        self.config = config
        self.current_file = current_file
        self.warnings: list[str] = []

    def rewrite_links(self, content: str) -> str:
        """Rewrite all links in markdown content.

        Args:
            content: Markdown content

        Returns:
            Content with rewritten links
        """
        # Rewrite markdown links [text](url)
        content = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)", self._rewrite_markdown_link, content
        )

        # Rewrite reference-style links [text][ref] and [ref]: url
        content = re.sub(
            r"^\[([^\]]+)\]:\s*(.+)$", self._rewrite_reference_link, content, flags=re.MULTILINE
        )

        return content

    def _rewrite_markdown_link(self, match: re.Match[str]) -> str:
        """Rewrite a single markdown link.

        Args:
            match: Regex match object

        Returns:
            Rewritten link
        """
        text = match.group(1)
        url = match.group(2)

        new_url = self._rewrite_url(url)
        return f"[{text}]({new_url})"

    def _rewrite_reference_link(self, match: re.Match[str]) -> str:
        """Rewrite a reference-style link definition.

        Args:
            match: Regex match object

        Returns:
            Rewritten link definition
        """
        ref = match.group(1)
        url = match.group(2)

        new_url = self._rewrite_url(url)
        return f"[{ref}]: {new_url}"

    def _rewrite_url(self, url: str) -> str:
        """Rewrite a single URL.

        Args:
            url: Original URL

        Returns:
            Rewritten URL
        """
        # Skip external URLs
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https", "ftp", "mailto"):
            return url

        # Skip anchors
        if url.startswith("#"):
            # Normalize anchor
            return self._normalize_anchor(url)

        # Handle document references
        url_path = Path(unquote(url.split("#")[0])) if "#" in url else Path(unquote(url))
        anchor = "#" + url.split("#")[1] if "#" in url else ""

        # Check if this is a reference to a converted document
        if url_path.suffix.lower() in [".docx", ".pdf", ".xlsx", ".doc", ".xls"]:
            # Try to find the converted markdown file
            converted_path = self._find_converted_file(url_path)
            if converted_path:
                # Calculate relative path from current file to converted file
                try:
                    rel_path = converted_path.relative_to(self.current_file.parent)
                    return str(rel_path).replace("\\", "/") + anchor
                except ValueError:
                    # Files are not in relative paths, use absolute from docs root
                    try:
                        rel_path = converted_path.relative_to(self.config.output_dir)
                        return "/" + str(rel_path).replace("\\", "/") + anchor
                    except ValueError:
                        pass

            # Couldn't find converted file
            self.warnings.append(f"Unresolved document link: {url}")
            return url

        return url

    def _find_converted_file(self, source_path: Path) -> Optional[Path]:
        """Find the converted markdown file for a source document.

        Args:
            source_path: Original source file path

        Returns:
            Path to converted markdown file, or None
        """
        # Check in converted files mapping
        for src, dest in self.config.converted_files.items():
            if src.name == source_path.name or str(src).endswith(str(source_path)):
                return dest

        return None

    def _normalize_anchor(self, anchor: str) -> str:
        """Normalize an anchor link for MkDocs.

        Args:
            anchor: Anchor string (e.g., "#my-heading")

        Returns:
            Normalized anchor
        """
        # MkDocs converts headings to lowercase and replaces spaces with hyphens
        if anchor.startswith("#"):
            anchor_text = anchor[1:]
            normalized = anchor_text.lower().replace(" ", "-")
            # Remove special characters
            normalized = re.sub(r"[^a-z0-9\-]", "", normalized)
            return f"#{normalized}"

        return anchor

