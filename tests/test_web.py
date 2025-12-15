"""Tests for web UI."""

import io
from pathlib import Path

import pytest

# Skip tests if web dependencies not installed
pytest.importorskip("fastapi")
pytest.importorskip("uvicorn")

from fastapi.testclient import TestClient

from doc2mkdocs.web import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_docx_bytes():
    """Create minimal DOCX file bytes."""
    # This is a minimal valid DOCX file structure
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        # Add minimal required files
        zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        zf.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships/>')
        zf.writestr(
            "word/document.xml",
            '<?xml version="1.0"?><document><body><p><t>Test</t></p></body></document>',
        )

    buffer.seek(0)
    return buffer.getvalue()


def test_root_endpoint(client):
    """Test root endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_validate_supported_file(client):
    """Test file validation with supported file type."""
    files = {"file": ("test.docx", b"fake content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/validate", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["extension"] == ".docx"


def test_validate_unsupported_file(client):
    """Test file validation with unsupported file type."""
    files = {"file": ("test.txt", b"fake content", "text/plain")}
    response = client.post("/api/validate", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["valid"] is False
    assert "Unsupported file type" in data["error"]


def test_validate_empty_file(client):
    """Test file validation with empty file."""
    files = {"file": ("test.docx", b"", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/validate", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["valid"] is False
    assert "empty" in data["error"].lower()


def test_upload_files(client, sample_docx_bytes):
    """Test file upload endpoint."""
    files = [
        ("files", ("test1.docx", sample_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"
    assert data["file_count"] == 1


def test_upload_oversized_file(client):
    """Test upload with file exceeding size limit."""
    # Create a file larger than 50MB
    large_content = b"x" * (51 * 1024 * 1024)
    files = [
        ("files", ("large.docx", large_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    response = client.post("/api/upload", files=files)

    assert response.status_code == 413


def test_status_nonexistent_job(client):
    """Test status endpoint with nonexistent job."""
    response = client.get("/api/status/nonexistent-job-id")
    assert response.status_code == 404


def test_download_nonexistent_job(client):
    """Test download endpoint with nonexistent job."""
    response = client.get("/api/download/nonexistent-job-id")
    assert response.status_code == 404


def test_delete_job(client, sample_docx_bytes):
    """Test job deletion."""
    # First upload a file
    files = [
        ("files", ("test.docx", sample_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    upload_response = client.post("/api/upload", files=files)
    job_id = upload_response.json()["job_id"]

    # Delete the job
    delete_response = client.delete(f"/api/job/{job_id}")
    assert delete_response.status_code == 200

    # Verify job is deleted
    status_response = client.get(f"/api/status/{job_id}")
    assert status_response.status_code == 404


def test_upload_multiple_files(client, sample_docx_bytes):
    """Test uploading multiple files."""
    files = [
        ("files", ("test1.docx", sample_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", ("test2.docx", sample_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_count"] == 2


def test_conversion_workflow(client, sample_docx_bytes):
    """Test complete conversion workflow."""
    # Upload file
    files = [
        ("files", ("test.docx", sample_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    upload_response = client.post("/api/upload", files=files)
    assert upload_response.status_code == 200

    job_id = upload_response.json()["job_id"]

    # Check status (may need to wait for processing)
    import time

    max_wait = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_response = client.get(f"/api/status/{job_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        if status_data["status"] in ["completed", "failed"]:
            break

        time.sleep(0.5)

    # Verify final status
    assert status_data["status"] in ["completed", "failed"]

