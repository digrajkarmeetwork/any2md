"""PDF to Markdown converter."""

import io
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image

from doc2mkdocs.core.base_converter import BaseConverter, ConversionResult
from doc2mkdocs.core.config import ConversionConfig, PDFOCRMode

logger = logging.getLogger(__name__)


class PdfConverter(BaseConverter):
    """Convert PDF files to Markdown."""

    SCANNED_TEXT_THRESHOLD = 100  # Minimum characters to consider PDF as text-based

    @property
    def supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions
        """
        return [".pdf"]

    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the file.

        Args:
            file_path: Path to file

        Returns:
            True if file can be converted
        """
        return file_path.suffix.lower() in self.supported_extensions

    def convert(self, file_path: Path) -> ConversionResult:
        """Convert PDF to Markdown.

        Args:
            file_path: Path to PDF file

        Returns:
            Conversion result
        """
        result = ConversionResult(success=True)

        try:
            doc = fitz.open(file_path)

            # Extract text
            text_content = []
            total_text_length = 0

            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()
                total_text_length += len(page_text.strip())
                text_content.append(page_text)

            # Detect if PDF is scanned
            is_scanned = total_text_length < self.SCANNED_TEXT_THRESHOLD

            if is_scanned:
                result.add_warning(
                    f"PDF appears to be scanned (only {total_text_length} characters extracted)"
                )

            # Determine if we should use OCR
            should_ocr = (
                self.config.pdf_ocr == PDFOCRMode.ON
                or (self.config.pdf_ocr == PDFOCRMode.AUTO and is_scanned)
            )

            if should_ocr:
                logger.info(f"Attempting OCR on {file_path}")
                markdown, images = self._convert_with_ocr(doc)
                result.markdown_content = markdown
                result.images = images
                result.add_warning("Used OCR for text extraction (quality may vary)")
            else:
                # Use extracted text
                markdown, images = self._convert_text_based(doc, text_content)
                result.markdown_content = markdown
                result.images = images

            # Extract metadata
            metadata = doc.metadata
            if metadata.get("title"):
                result.metadata["title"] = metadata["title"]
            else:
                result.metadata["title"] = file_path.stem.replace("-", " ").title()

            if metadata.get("author"):
                result.metadata["author"] = metadata["author"]

            # Quality heuristics
            if is_scanned and not should_ocr:
                result.quality_score = 0.3
            elif is_scanned and should_ocr:
                result.quality_score = 0.6

            doc.close()

        except Exception as e:
            logger.error(f"Failed to convert {file_path}: {e}")
            result.add_error(f"Conversion failed: {str(e)}")

        return result

    def _convert_text_based(
        self, doc: fitz.Document, text_content: list[str]
    ) -> tuple[str, dict[str, bytes]]:
        """Convert PDF using extracted text.

        Args:
            doc: PDF document
            text_content: Extracted text per page

        Returns:
            Tuple of (markdown content, images dict)
        """
        images: dict[str, bytes] = {}
        markdown_parts = []

        for page_num, (page, page_text) in enumerate(zip(doc, text_content), start=1):
            # Add page heading
            if len(doc) > 1:
                markdown_parts.append(f"\n## Page {page_num}\n")

            # Add text
            markdown_parts.append(page_text)

            # Extract images from page
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    image_name = f"page-{page_num}-image-{img_index + 1}.{image_ext}"
                    images[image_name] = image_bytes

                    # Add image reference to markdown
                    markdown_parts.append(f"\n![Image {img_index + 1}]({image_name})\n")

                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")

        markdown = "\n".join(markdown_parts)
        return markdown, images

    def _convert_with_ocr(self, doc: fitz.Document) -> tuple[str, dict[str, bytes]]:
        """Convert PDF using OCR.

        Args:
            doc: PDF document

        Returns:
            Tuple of (markdown content, images dict)
        """
        try:
            import pytesseract
        except ImportError:
            raise RuntimeError(
                "pytesseract is required for OCR but not installed. "
                "Install with: pip install pytesseract"
            )

        images: dict[str, bytes] = {}
        markdown_parts = []

        for page_num, page in enumerate(doc, start=1):
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")

            # Save page image
            page_image_name = f"page-{page_num}.png"
            images[page_image_name] = img_data

            # Perform OCR
            try:
                img = Image.open(io.BytesIO(img_data))
                ocr_text = pytesseract.image_to_string(img)

                if len(doc) > 1:
                    markdown_parts.append(f"\n## Page {page_num}\n")

                markdown_parts.append(ocr_text)
                markdown_parts.append(f"\n![Page {page_num}]({page_image_name})\n")

            except Exception as e:
                logger.warning(f"OCR failed for page {page_num}: {e}")
                markdown_parts.append(f"\n_[OCR failed for this page]_\n")
                markdown_parts.append(f"\n![Page {page_num}]({page_image_name})\n")

        markdown = "\n".join(markdown_parts)
        return markdown, images

