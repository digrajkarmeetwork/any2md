"""Command-line interface for doc2mkdocs."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from doc2mkdocs.converters import DocxConverter, PdfConverter, XlsxConverter
from doc2mkdocs.core.base_converter import BaseConverter
from doc2mkdocs.core.config import ConversionConfig, ExcelMode, PDFOCRMode
from doc2mkdocs.core.report import ConversionReport, FileReport
from doc2mkdocs.normalizer import ImageHandler, LinkRewriter, MarkdownNormalizer
from doc2mkdocs.utils import sanitize_filename, setup_logger
from doc2mkdocs.utils.filename_sanitizer import get_unique_filename

app = typer.Typer(
    name="doc2mkdocs",
    help="Convert documentation files (DOCX, PDF, XLSX) into MkDocs-ready Markdown",
)
console = Console()


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Input file or directory to convert"),
    out: Path = typer.Option("docs", "--out", help="Output directory"),
    assets_dir: Optional[Path] = typer.Option(None, "--assets-dir", help="Assets directory"),
    split_by_heading: bool = typer.Option(False, "--split-by-heading", help="Split long docs by heading"),
    excel_mode: ExcelMode = typer.Option(ExcelMode.SHEET_PER_PAGE, "--excel-mode", help="Excel conversion mode"),
    pdf_ocr: PDFOCRMode = typer.Option(PDFOCRMode.AUTO, "--pdf-ocr", help="PDF OCR mode"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files"),
    front_matter: bool = typer.Option(True, "--front-matter/--no-front-matter", help="Add YAML front matter"),
    mkdocs_nav: bool = typer.Option(False, "--mkdocs-nav", help="Generate mkdocs.yml nav snippet"),
    report_path: Optional[Path] = typer.Option(None, "--report", help="Report output path"),
    log_level: str = typer.Option("info", "--log-level", help="Log level"),
) -> None:
    """Convert documentation files to MkDocs-ready Markdown."""
    # Setup logging
    logger = setup_logger(level=log_level.upper())

    # Create configuration
    config = ConversionConfig(
        input_path=input_path,
        output_dir=out,
        assets_dir=assets_dir,
        split_by_heading=split_by_heading,
        excel_mode=excel_mode,
        pdf_ocr=pdf_ocr,
        overwrite=overwrite,
        front_matter=front_matter,
        mkdocs_nav=mkdocs_nav,
        report_path=report_path,
        log_level=log_level,
    )

    # Initialize converters
    converters: list[BaseConverter] = [
        DocxConverter(config),
        PdfConverter(config),
        XlsxConverter(config),
    ]

    # Initialize report
    report = ConversionReport()

    # Collect files to convert
    files_to_convert = _collect_files(input_path, converters)

    if not files_to_convert:
        console.print("[yellow]No convertible files found.[/yellow]")
        return

    console.print(f"[green]Found {len(files_to_convert)} file(s) to convert[/green]")

    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Convert files
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Converting files...", total=len(files_to_convert))

        for file_path, converter in files_to_convert:
            progress.update(task, description=f"Converting {file_path.name}...")

            start_time = time.time()
            file_report = _convert_file(file_path, converter, config)
            file_report.conversion_time_ms = (time.time() - start_time) * 1000

            report.add_file_report(file_report)
            progress.advance(task)

    # Finalize report
    report.finalize()

    # Save report
    report.to_json(config.report_path)
    console.print(f"\n[green]Report saved to {config.report_path}[/green]")

    # Print summary
    console.print("\n" + report.to_text())

    # Generate mkdocs nav if requested
    if config.mkdocs_nav:
        _generate_mkdocs_nav(config, report)


def _collect_files(
    input_path: Path, converters: list[BaseConverter]
) -> list[tuple[Path, BaseConverter]]:
    """Collect files to convert.

    Args:
        input_path: Input file or directory
        converters: List of available converters

    Returns:
        List of (file_path, converter) tuples
    """
    files_to_convert = []

    if input_path.is_file():
        # Single file
        for converter in converters:
            if converter.can_convert(input_path):
                files_to_convert.append((input_path, converter))
                break
    elif input_path.is_dir():
        # Directory - recursive search
        for file_path in input_path.rglob("*"):
            if file_path.is_file():
                for converter in converters:
                    if converter.can_convert(file_path):
                        files_to_convert.append((file_path, converter))
                        break

    return files_to_convert


def _convert_file(
    file_path: Path, converter: BaseConverter, config: ConversionConfig
) -> FileReport:
    """Convert a single file.

    Args:
        file_path: Path to file
        converter: Converter to use
        config: Conversion configuration

    Returns:
        File report
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Converting {file_path}")

    # Perform conversion
    result = converter.convert(file_path)

    if not result.success:
        return FileReport(
            source_file=str(file_path),
            output_file=None,
            success=False,
            errors=result.errors,
            warnings=result.warnings,
            quality_score=result.quality_score,
            converter_used=converter.__class__.__name__,
        )

    # Normalize markdown
    normalizer = MarkdownNormalizer()
    markdown = result.markdown_content

    # Normalize headings
    markdown, heading_warnings = normalizer.normalize_headings(markdown)
    result.warnings.extend(heading_warnings)

    # Normalize whitespace
    markdown = normalizer.normalize_whitespace(markdown)

    # Determine output path
    output_path = _get_output_path(file_path, config)

    # Handle images
    image_handler = ImageHandler(config, file_path.name)
    image_mapping = image_handler.save_images(result.images, output_path)
    markdown = image_handler.rewrite_image_paths(markdown, image_mapping)

    # Rewrite links
    link_rewriter = LinkRewriter(config, output_path)
    markdown = link_rewriter.rewrite_links(markdown)
    result.warnings.extend(link_rewriter.warnings)

    # Add front matter if requested
    if config.front_matter:
        title = result.metadata.get("title", file_path.stem.replace("-", " ").title())
        markdown = normalizer.add_front_matter(
            markdown,
            title=title,
            source=str(file_path),
            converted_at=datetime.now().isoformat(),
            **{k: v for k, v in result.metadata.items() if k != "title"},
        )

    # Write output file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not config.overwrite:
        output_path = get_unique_filename(output_path.parent, output_path.name)

    output_path.write_text(markdown, encoding="utf-8")

    # Track converted file
    config.converted_files[file_path] = output_path

    logger.info(f"Converted {file_path} -> {output_path}")

    return FileReport(
        source_file=str(file_path),
        output_file=str(output_path),
        success=True,
        warnings=result.warnings,
        errors=result.errors,
        quality_score=result.quality_score,
        converter_used=converter.__class__.__name__,
    )


def _get_output_path(file_path: Path, config: ConversionConfig) -> Path:
    """Determine output path for a converted file.

    Args:
        file_path: Source file path
        config: Conversion configuration

    Returns:
        Output markdown file path
    """
    # Sanitize filename
    sanitized_name = sanitize_filename(file_path.stem) + ".md"

    # Preserve directory structure if input is a directory
    if config.input_path.is_dir():
        try:
            rel_path = file_path.parent.relative_to(config.input_path)
            output_dir = config.output_dir / rel_path
        except ValueError:
            output_dir = config.output_dir
    else:
        output_dir = config.output_dir

    return output_dir / sanitized_name


def _generate_mkdocs_nav(config: ConversionConfig, report: ConversionReport) -> None:
    """Generate mkdocs.yml nav snippet.

    Args:
        config: Conversion configuration
        report: Conversion report
    """
    nav_file = config.output_dir / "mkdocs-nav-snippet.yml"

    nav_lines = ["nav:"]

    # Group files by directory
    files_by_dir: dict[str, list[str]] = {}

    for file_report in report.files:
        if file_report.success and file_report.output_file:
            output_path = Path(file_report.output_file)
            try:
                rel_path = output_path.relative_to(config.output_dir)
                dir_name = str(rel_path.parent) if rel_path.parent != Path(".") else "root"

                if dir_name not in files_by_dir:
                    files_by_dir[dir_name] = []

                files_by_dir[dir_name].append(str(rel_path))
            except ValueError:
                continue

    # Generate nav structure
    for dir_name in sorted(files_by_dir.keys()):
        if dir_name == "root":
            for file_path in sorted(files_by_dir[dir_name]):
                title = Path(file_path).stem.replace("-", " ").title()
                nav_lines.append(f"  - {title}: {file_path}")
        else:
            nav_lines.append(f"  - {dir_name.replace('-', ' ').title()}:")
            for file_path in sorted(files_by_dir[dir_name]):
                title = Path(file_path).stem.replace("-", " ").title()
                nav_lines.append(f"    - {title}: {file_path}")

    nav_content = "\n".join(nav_lines)
    nav_file.write_text(nav_content, encoding="utf-8")

    console.print(f"[green]MkDocs nav snippet saved to {nav_file}[/green]")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the web UI server."""
    try:
        import uvicorn
        from doc2mkdocs.web import create_app
    except ImportError:
        console.print(
            "[red]Web UI dependencies not installed.[/red]\n"
            "Install with: [cyan]pip install doc2mkdocs[web][/cyan]"
        )
        raise typer.Exit(1)

    console.print(f"[green]Starting doc2mkdocs web UI...[/green]")
    console.print(f"[cyan]Open your browser to: http://{host}:{port}[/cyan]\n")

    # Create app
    web_app = create_app()

    # Run server
    uvicorn.run(
        web_app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    app()

