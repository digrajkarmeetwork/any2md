"""Core components for doc2mkdocs."""

from doc2mkdocs.core.base_converter import BaseConverter, ConversionResult
from doc2mkdocs.core.config import ConversionConfig, ExcelMode, PDFOCRMode
from doc2mkdocs.core.report import ConversionReport, FileReport

__all__ = [
    "BaseConverter",
    "ConversionResult",
    "ConversionConfig",
    "ExcelMode",
    "PDFOCRMode",
    "ConversionReport",
    "FileReport",
]

