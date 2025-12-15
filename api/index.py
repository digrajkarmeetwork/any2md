"""
Vercel serverless function entry point for doc2mkdocs web UI.
"""

import sys
import os
from pathlib import Path

# Add src to path
root_path = Path(__file__).parent.parent
src_path = root_path / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(root_path))

# Import FastAPI and create app directly
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import uuid
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import json
import zipfile

# Create FastAPI app
app = FastAPI(title="doc2mkdocs Web UI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for conversion jobs
conversion_jobs: Dict[str, Dict[str, Any]] = {}

# Constants
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default
SUPPORTED_EXTENSIONS = {".docx", ".doc", ".pdf", ".xlsx", ".xls"}

@app.get("/")
async def root():
    """Serve the main page."""
    return {
        "message": "any2md API",
        "version": "1.0.0",
        "endpoints": {
            "validate": "POST /api/validate",
            "upload": "POST /api/upload",
            "status": "GET /api/status/{job_id}",
            "download": "GET /api/download/{job_id}",
            "delete": "DELETE /api/job/{job_id}"
        },
        "note": "Download the Windows app from GitHub releases."
    }

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/validate")
async def validate_file(file: UploadFile = File(...)):
    """Validate a file before upload."""
    try:
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "error": f"Unsupported file type: {file_ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
                }
            )

        # Check if file is empty
        content = await file.read(1024)  # Read first 1KB
        await file.seek(0)  # Reset file pointer

        if not content:
            return JSONResponse(
                status_code=400,
                content={"valid": False, "error": "File is empty"}
            )

        return {"valid": True, "filename": file.filename, "type": file_ext}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"valid": False, "error": str(e)}
        )

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files for conversion.
    Note: Full conversion may timeout on Vercel free tier (10s limit).
    Consider using the CLI for large files.
    """
    try:
        # Create job ID
        job_id = str(uuid.uuid4())

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())
        upload_dir = temp_dir / "uploads"
        upload_dir.mkdir(exist_ok=True)

        # Save uploaded files
        uploaded_files = []
        for file in files:
            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024}MB"
                    }
                )

            # Save file
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(content)

            uploaded_files.append({
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content)
            })

        # Store job info
        conversion_jobs[job_id] = {
            "status": "pending",
            "files": uploaded_files,
            "temp_dir": str(temp_dir),
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "message": "Files uploaded. Conversion not available in serverless mode."
        }

        return {
            "job_id": job_id,
            "files_count": len(uploaded_files),
            "message": "Files uploaded successfully. Note: Full conversion requires CLI due to Vercel timeout limits.",
            "recommendation": "Download the CLI tool from GitHub for full conversion capabilities."
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload failed: {str(e)}"}
        )

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get conversion job status."""
    if job_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = conversion_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
        "message": job.get("message", ""),
        "files_count": len(job.get("files", [])),
        "created_at": job.get("created_at")
    }

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a conversion job and cleanup files."""
    if job_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = conversion_jobs[job_id]

    # Cleanup temp directory
    if "temp_dir" in job:
        temp_dir = Path(job["temp_dir"])
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    # Remove from jobs
    del conversion_jobs[job_id]

    return {"message": "Job deleted successfully"}

# Handler for Vercel
handler = app

