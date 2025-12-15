# Web UI Guide

This guide covers the web-based user interface for doc2mkdocs.

## Installation

Install doc2mkdocs with web UI support:

```bash
pip install .[web]
```

This installs the following additional dependencies:
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **python-multipart**: File upload support

## Starting the Server

### Basic Usage

```bash
doc2mkdocs serve
```

This starts the server on `http://127.0.0.1:8000`. Open this URL in your browser.

### Custom Configuration

```bash
# Custom port
doc2mkdocs serve --port 3000

# Allow external connections
doc2mkdocs serve --host 0.0.0.0 --port 8080

# Development mode with auto-reload
doc2mkdocs serve --reload
```

## Using the Web Interface

### 1. Upload Files

**Drag and Drop:**
- Drag files from your file explorer directly onto the upload area
- Multiple files can be uploaded at once

**Click to Browse:**
- Click anywhere in the upload area
- Select one or more files from the file picker

**Supported Formats:**
- DOCX (Microsoft Word)
- PDF (Portable Document Format)
- XLSX (Microsoft Excel)

### 2. File Validation

After selecting files, each file is automatically validated:

- ✅ **Valid**: File type is supported and ready for conversion
- ❌ **Invalid**: File type is not supported or file is corrupted

You can remove invalid files by clicking the ✕ button.

### 3. Convert Files

Click the **"Convert Files"** button to start the conversion process.

The interface will show:
- A spinner animation
- Progress bar (0-100%)
- Current conversion status

### 4. View Results

After conversion completes, you'll see:

**Summary Statistics:**
- Total files processed
- Successful conversions
- Failed conversions
- Average quality score

**Individual File Reports:**
- Source filename
- Output filename
- Quality score (0-100%)
- Warnings (if any)
- Errors (if any)

**Quality Score Indicators:**
- 🟢 **High (80-100%)**: Excellent conversion quality
- 🟡 **Medium (50-79%)**: Good quality with minor issues
- 🔴 **Low (0-49%)**: Poor quality, manual review recommended

### 5. Download Results

Click the **"Download ZIP"** button to download all converted files.

**ZIP Contents:**
- All converted Markdown files
- `assets/` folder with extracted images
- `conversion-report.json` with detailed results

### 6. Convert More Files

Click **"Convert More Files"** to return to the upload screen and start a new conversion.

## Features

### File Size Limits

- Maximum file size: **50MB per file**
- Files exceeding this limit will be rejected with an error message

### Conversion Options

The web UI uses these default settings:
- **Excel Mode**: Sheet-per-page (each sheet becomes a separate section)
- **PDF OCR**: Auto (OCR is used for scanned PDFs)
- **Front Matter**: Enabled (YAML metadata added to each file)
- **Overwrite**: Enabled (existing files are replaced)

### Real-Time Progress

The interface polls the server every second to update:
- Conversion progress percentage
- Current status (processing, completed, failed)

### Automatic Cleanup

Temporary files are automatically deleted:
- 60 seconds after download
- When you start a new conversion
- When you close the browser (eventually)

## API Endpoints

The web UI is built on a REST API that you can also use programmatically:

### POST /api/validate

Validate a single file before upload.

**Request:**
```bash
curl -X POST http://localhost:8000/api/validate \
  -F "file=@document.docx"
```

**Response:**
```json
{
  "valid": true,
  "filename": "document.docx",
  "extension": ".docx",
  "message": "File is valid and ready for conversion"
}
```

### POST /api/upload

Upload files for conversion.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@document1.docx" \
  -F "files=@document2.pdf"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "file_count": 2
}
```

### GET /api/status/{job_id}

Check conversion status.

**Request:**
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "file_count": 2,
  "report": {
    "total_files": 2,
    "successful": 2,
    "failed": 0,
    "average_quality_score": 0.95
  }
}
```

### GET /api/download/{job_id}

Download conversion results as ZIP.

**Request:**
```bash
curl -O -J http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000
```

### DELETE /api/job/{job_id}

Delete a conversion job and its files.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/job/550e8400-e29b-41d4-a716-446655440000
```

## Troubleshooting

### Server Won't Start

**Error: "Web UI dependencies not installed"**

Solution:
```bash
pip install .[web]
```

**Error: "Address already in use"**

Solution: Use a different port
```bash
doc2mkdocs serve --port 8001
```

### Files Not Converting

**Check the browser console** (F12) for JavaScript errors.

**Check the server logs** in the terminal where you ran `doc2mkdocs serve`.

### Download Not Working

- Ensure the conversion completed successfully
- Check that your browser allows downloads
- Try a different browser if issues persist

### Large Files Timing Out

For files larger than 50MB, use the CLI instead:
```bash
doc2mkdocs convert large-file.pdf --out docs/
```

## Security Considerations

### Local Use Only

By default, the server binds to `127.0.0.1` (localhost), making it accessible only from your computer.

### External Access

If you use `--host 0.0.0.0`, the server will be accessible from other computers on your network. Only do this on trusted networks.

### File Cleanup

Uploaded files are stored temporarily and deleted after download. However, for sensitive documents, consider using the CLI instead.

## Performance

### Concurrent Conversions

The web UI processes one job at a time. Multiple users can upload files, but conversions are queued.

### Memory Usage

Each conversion job uses temporary disk space. Large batches of files may require significant disk space.

### Recommended Limits

- **Files per upload**: 10-20 files
- **Total size per upload**: 200-500MB
- **Concurrent users**: 1-5 users

For larger batches, use the CLI with parallel processing (future feature).

## Development

### Running in Development Mode

```bash
doc2mkdocs serve --reload
```

This enables auto-reload when you modify the code.

### Customizing the UI

The web UI files are located in:
- `src/doc2mkdocs/web/app.py` - FastAPI backend
- `src/doc2mkdocs/web/static/index.html` - HTML structure
- `src/doc2mkdocs/web/static/style.css` - Styling
- `src/doc2mkdocs/web/static/app.js` - JavaScript logic

### Adding Features

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to the web UI.

