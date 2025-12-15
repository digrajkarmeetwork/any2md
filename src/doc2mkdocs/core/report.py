"""Conversion reporting functionality."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class FileReport:
    """Report for a single file conversion."""

    source_file: str
    output_file: Optional[str]
    success: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    quality_score: float = 1.0
    converter_used: str = ""
    conversion_time_ms: float = 0.0


@dataclass
class ConversionReport:
    """Overall conversion report."""

    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    files: list[FileReport] = field(default_factory=list)
    average_quality_score: float = 0.0

    def add_file_report(self, report: FileReport) -> None:
        """Add a file report to the overall report.

        Args:
            report: File report to add
        """
        self.files.append(report)
        self.total_files += 1
        if report.success:
            self.successful += 1
        else:
            self.failed += 1
        self._update_average_quality()

    def finalize(self) -> None:
        """Finalize the report with end time."""
        self.end_time = datetime.now().isoformat()

    def _update_average_quality(self) -> None:
        """Update the average quality score."""
        if self.files:
            self.average_quality_score = sum(f.quality_score for f in self.files) / len(
                self.files
            )

    def to_json(self, path: Path) -> None:
        """Save report as JSON.

        Args:
            path: Path to save JSON report
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    def to_text(self) -> str:
        """Generate human-readable text report.

        Returns:
            Formatted text report
        """
        lines = [
            "=" * 80,
            "CONVERSION REPORT",
            "=" * 80,
            f"Started:  {self.start_time}",
            f"Finished: {self.end_time or 'In progress'}",
            "",
            f"Total files:     {self.total_files}",
            f"Successful:      {self.successful}",
            f"Failed:          {self.failed}",
            f"Average quality: {self.average_quality_score:.2f}",
            "",
            "=" * 80,
            "FILE DETAILS",
            "=" * 80,
        ]

        for file_report in self.files:
            status = "✓ SUCCESS" if file_report.success else "✗ FAILED"
            lines.append(f"\n{status} - {file_report.source_file}")
            lines.append(f"  Output: {file_report.output_file or 'N/A'}")
            lines.append(f"  Quality: {file_report.quality_score:.2f}")
            lines.append(f"  Converter: {file_report.converter_used}")
            lines.append(f"  Time: {file_report.conversion_time_ms:.0f}ms")

            if file_report.warnings:
                lines.append(f"  Warnings ({len(file_report.warnings)}):")
                for warning in file_report.warnings:
                    lines.append(f"    - {warning}")

            if file_report.errors:
                lines.append(f"  Errors ({len(file_report.errors)}):")
                for error in file_report.errors:
                    lines.append(f"    - {error}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

