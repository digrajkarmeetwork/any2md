"""doc2mkdocs - Convert documentation files into MkDocs-ready Markdown."""

__version__ = "1.0.0"
__author__ = "doc2mkdocs contributors"
__license__ = "MIT"

from doc2mkdocs.core.base_converter import BaseConverter
from doc2mkdocs.core.config import ConversionConfig
from doc2mkdocs.core.report import ConversionReport

__all__ = ["BaseConverter", "ConversionConfig", "ConversionReport", "__version__"]

