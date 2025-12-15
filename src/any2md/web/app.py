"""FastAPI web application for doc2mkdocs."""

import asyncio
import logging
import shutil
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from doc2mkdocs.converters import DocxConverter, PdfConverter, XlsxConverter
from doc2mkdocs.core.base_converter import BaseConverter
from doc2mkdocs.core.config import ConversionConfig, ExcelMode, PDFOCRMode
from doc2mkdocs.core.report import ConversionReport, FileReport
from doc2mkdocs.normalizer import ImageHandler, LinkRewriter, MarkdownNormalizer
from doc2mkdocs.utils import sanitize_filename, setup_logger
from doc2mkdocs.utils.filename_sanitizer import get_unique_filename

logger = setup_logger("doc2mkdocs.web")

# Store active conversion jobs
conversion_jobs: dict[str, dict[str, Any]] = {}

# Maximum file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Supported extensions
SUPPORTED_EXTENSIONS = {".docx", ".doc", ".pdf", ".xlsx", ".xls"}


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="doc2mkdocs Web UI",
        description="Convert documentation files to MkDocs-ready Markdown",
        version="1.0.0",
    )

    # Get static files directory
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        """Serve the main HTML page."""
        html_file = static_dir / "index.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>doc2mkdocs Web UI</h1><p>Static files not found.</p>")

    @app.post("/api/validate")
    async def validate_file(file: UploadFile = File(...)) -> JSONResponse:
        """Validate uploaded file.

        Args:
            file: Uploaded file

        Returns:
            Validation result
        """
        try:
            # Check file extension
            file_path = Path(file.filename or "unknown")
            extension = file_path.suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                return JSONResponse(
                    status_code=400,
                    content={
                        "valid": False,
                        "error": f"Unsupported file type: {extension}",
                        "supported": list(SUPPORTED_EXTENSIONS),
                    },
                )

            # Check file size (read first chunk to estimate)
            chunk = await file.read(1024)
            await file.seek(0)

            if not chunk:
                return JSONResponse(
                    status_code=400,
                    content={"valid": False, "error": "File is empty"},
                )

            return JSONResponse(
                content={
                    "valid": True,
                    "filename": file.filename,
                    "extension": extension,
                    "message": "File is valid and ready for conversion",
                }
            )

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return JSONResponse(
                status_code=500,
                content={"valid": False, "error": f"Validation failed: {str(e)}"},
            )

    @app.post("/api/upload")
    async def upload_files(files: list[UploadFile] = File(...)) -> JSONResponse:
        """Upload and convert files.

        Args:
            files: List of uploaded files

        Returns:
            Job ID for tracking conversion
        """
        try:
            # Generate job ID
            job_id = str(uuid.uuid4())

            # Create temporary directory for this job
            temp_dir = Path(tempfile.mkdtemp(prefix=f"doc2mkdocs_{job_id}_"))
            input_dir = temp_dir / "input"
            output_dir = temp_dir / "output"
            input_dir.mkdir()
            output_dir.mkdir()

            # Save uploaded files
            uploaded_files = []
            for file in files:
                if not file.filename:
                    continue

                # Check file size
                content = await file.read()
                if len(content) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File {file.filename} exceeds maximum size of 50MB",
                    )

                # Save file
                file_path = input_dir / file.filename
                file_path.write_bytes(content)
                uploaded_files.append(file_path)

            # Initialize job
            conversion_jobs[job_id] = {
                "status": "processing",
                "temp_dir": temp_dir,
                "input_dir": input_dir,
                "output_dir": output_dir,
                "files": uploaded_files,
                "created_at": datetime.now().isoformat(),
                "progress": 0,
            }

            # Start conversion in background
            asyncio.create_task(process_conversion(job_id))

            return JSONResponse(
                content={
                    "job_id": job_id,
                    "status": "processing",
                    "file_count": len(uploaded_files),
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    @app.get("/api/status/{job_id}")
    async def get_status(job_id: str) -> JSONResponse:
        """Get conversion job status.

        Args:
            job_id: Job ID

        Returns:
            Job status and progress
        """
        if job_id not in conversion_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = conversion_jobs[job_id]

        return JSONResponse(
            content={
                "job_id": job_id,
                "status": job["status"],
                "progress": job.get("progress", 0),
                "file_count": len(job.get("files", [])),
                "report": job.get("report"),
                "error": job.get("error"),
            }
        )

    @app.get("/api/download/{job_id}")
    async def download_result(job_id: str) -> FileResponse:
        """Download conversion results as ZIP.

        Args:
            job_id: Job ID

        Returns:
            ZIP file with converted documents
        """
        if job_id not in conversion_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = conversion_jobs[job_id]

        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail="Conversion not completed")

        # Create ZIP file
        output_dir = job["output_dir"]
        zip_path = job["temp_dir"] / "result.zip"

        shutil.make_archive(
            str(zip_path.with_suffix("")), "zip", output_dir
        )

        # Schedule cleanup after download
        asyncio.create_task(cleanup_job(job_id, delay=60))

        return FileResponse(
            path=str(zip_path),
            media_type="application/zip",
            filename=f"doc2mkdocs-{job_id[:8]}.zip",
        )

    @app.delete("/api/job/{job_id}")
    async def delete_job(job_id: str) -> JSONResponse:
        """Delete a conversion job.

        Args:
            job_id: Job ID

        Returns:
            Deletion confirmation
        """
        if job_id not in conversion_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        await cleanup_job(job_id, delay=0)

        return JSONResponse(content={"message": "Job deleted successfully"})

    return app


async def process_conversion(job_id: str) -> None:
    """Process file conversion in background.

    Args:
        job_id: Job ID
    """
    try:
        job = conversion_jobs[job_id]
        input_dir = job["input_dir"]
        output_dir = job["output_dir"]

        # Create configuration
        config = ConversionConfig(
            input_path=input_dir,
            output_dir=output_dir,
            excel_mode=ExcelMode.SHEET_PER_PAGE,
            pdf_ocr=PDFOCRMode.AUTO,
            overwrite=True,
            front_matter=True,
            mkdocs_nav=False,
            log_level="info",
        )

        # Initialize converters
        converters: list[BaseConverter] = [
            DocxConverter(config),
            PdfConverter(config),
            XlsxConverter(config),
        ]

        # Initialize report
        report = ConversionReport()

        # Process files
        files = job["files"]
        total_files = len(files)

        for idx, file_path in enumerate(files):
            # Update progress
            job["progress"] = int((idx / total_files) * 100)

            # Find appropriate converter
            converter = None
            for conv in converters:
                if conv.can_convert(file_path):
                    converter = conv
                    break

            if not converter:
                file_report = FileReport(
                    source_file=str(file_path),
                    output_file=None,
                    success=False,
                    errors=[f"No converter found for {file_path.suffix}"],
                    converter_used="None",
                )
                report.add_file_report(file_report)
                continue

            # Convert file
            start_time = time.time()
            file_report = await asyncio.to_thread(
                convert_single_file, file_path, converter, config
            )
            file_report.conversion_time_ms = (time.time() - start_time) * 1000
            report.add_file_report(file_report)

        # Finalize report
        report.finalize()

        # Save report
        report_path = output_dir / "conversion-report.json"
        report.to_json(report_path)

        # Update job status
        job["status"] = "completed"
        job["progress"] = 100
        job["report"] = {
            "total_files": report.total_files,
            "successful": report.successful,
            "failed": report.failed,
            "average_quality_score": report.average_quality_score,
            "files": [
                {
                    "source_file": f.source_file,
                    "output_file": f.output_file,
                    "success": f.success,
                    "warnings": f.warnings,
                    "errors": f.errors,
                    "quality_score": f.quality_score,
                }
                for f in report.files
            ],
        }

    except Exception as e:
        logger.error(f"Conversion error for job {job_id}: {e}")
        job["status"] = "failed"
        job["error"] = str(e)


def convert_single_file(
    file_path: Path, converter: BaseConverter, config: ConversionConfig
) -> FileReport:
    """Convert a single file (synchronous).

    Args:
        file_path: Path to file
        converter: Converter to use
        config: Conversion configuration

    Returns:
        File report
    """
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
    sanitized_name = sanitize_filename(file_path.stem) + ".md"
    output_path = config.output_dir / sanitized_name

    # Handle images
    image_handler = ImageHandler(config, file_path.name)
    image_mapping = image_handler.save_images(result.images, output_path)
    markdown = image_handler.rewrite_image_paths(markdown, image_mapping)

    # Rewrite links
    link_rewriter = LinkRewriter(config, output_path)
    markdown = link_rewriter.rewrite_links(markdown)
    result.warnings.extend(link_rewriter.warnings)

    # Add front matter
    if config.front_matter:
        title = result.metadata.get("title", file_path.stem.replace("-", " ").title())
        markdown = normalizer.add_front_matter(
            markdown,
            title=title,
            source=str(file_path.name),
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
        source_file=str(file_path.name),
        output_file=str(output_path.name),
        success=True,
        warnings=result.warnings,
        errors=result.errors,
        quality_score=result.quality_score,
        converter_used=converter.__class__.__name__,
    )


async def cleanup_job(job_id: str, delay: int = 0) -> None:
    """Clean up job files after delay.

    Args:
        job_id: Job ID
        delay: Delay in seconds before cleanup
    """
    if delay > 0:
        await asyncio.sleep(delay)

    if job_id in conversion_jobs:
        job = conversion_jobs[job_id]
        temp_dir = job.get("temp_dir")

        if temp_dir and Path(temp_dir).exists():
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up job {job_id}")
            except Exception as e:
                logger.error(f"Failed to clean up job {job_id}: {e}")

        del conversion_jobs[job_id]


