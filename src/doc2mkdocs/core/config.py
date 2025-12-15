"""Configuration classes for doc2mkdocs."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ExcelMode(str, Enum):
    """Excel conversion mode."""

    SHEET_PER_PAGE = "sheet-per-page"
    SINGLE_PAGE = "single-page"


class PDFOCRMode(str, Enum):
    """PDF OCR mode."""

    OFF = "off"
    AUTO = "auto"
    ON = "on"


@dataclass
class ConversionConfig:
    """Configuration for document conversion."""

    input_path: Path
    output_dir: Path
    assets_dir: Optional[Path] = None
    split_by_heading: bool = False
    excel_mode: ExcelMode = ExcelMode.SHEET_PER_PAGE
    pdf_ocr: PDFOCRMode = PDFOCRMode.AUTO
    overwrite: bool = False
    front_matter: bool = True
    mkdocs_nav: bool = False
    report_path: Optional[Path] = None
    log_level: str = "info"
    
    # Internal tracking
    converted_files: dict[Path, Path] = field(default_factory=dict)
    """Maps source file paths to output markdown paths."""

    def __post_init__(self) -> None:
        """Initialize computed fields."""
        if self.assets_dir is None:
            self.assets_dir = self.output_dir / "assets"
        if self.report_path is None:
            self.report_path = self.output_dir / "conversion-report.json"
        
        # Ensure paths are Path objects
        self.input_path = Path(self.input_path)
        self.output_dir = Path(self.output_dir)
        self.assets_dir = Path(self.assets_dir)
        self.report_path = Path(self.report_path)

