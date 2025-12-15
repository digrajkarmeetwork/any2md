# 🚀 START HERE - doc2mkdocs Web UI

Welcome! This guide will get you up and running with the doc2mkdocs web interface in **under 5 minutes**.

## ✅ What You Have

A complete, production-ready web application for converting documents (DOCX, PDF, XLSX) to MkDocs-ready Markdown with:

- 🖱️ Drag-and-drop file upload
- ✅ Real-time file validation  
- 📊 Live conversion progress
- 📈 Quality scores and warnings
- 📦 Download results as ZIP
- 🎨 Clean, responsive interface

## 📋 Prerequisites

You need:
- **Python 3.11+** installed
- **pip** (Python package manager)

Check if you have Python:
```bash
python --version
# or
python3 --version
```

## 🏃 Quick Start (3 Steps)

### Step 1: Install Dependencies

Open a terminal in this directory and run:

```bash
pip install fastapi uvicorn python-multipart mammoth pymupdf openpyxl pyyaml typer rich
```

**Or** install everything at once:
```bash
pip install -e ".[web]"
```

### Step 2: Start the Server

**Windows:**
```bash
# Double-click: start_web_ui.bat
# Or run:
python start_web_ui.py
```

**macOS/Linux:**
```bash
python3 start_web_ui.py
```

You should see:
```
🚀 Starting doc2mkdocs Web UI...
📂 Open your browser to: http://127.0.0.1:8000
⏹️  Press CTRL+C to stop

INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Open Your Browser

Go to: **http://127.0.0.1:8000**

🎉 **You're ready to convert documents!**

## 📖 How to Use

1. **Drag files** onto the upload area (or click to browse)
2. Wait for **validation** (green ✓ = ready)
3. Click **"Convert Files"**
4. Watch the **progress bar**
5. Review **quality scores** and warnings
6. Click **"Download ZIP"**

## 📁 What's Inside the ZIP?

```
doc2mkdocs-xxxxx.zip
├── your-document.md          # Converted Markdown
├── another-file.md           # More converted files
├── assets/                   # Extracted images
│   ├── your-document/
│   │   ├── image-001.png
│   │   └── image-002.png
│   └── another-file/
│       └── diagram-001.png
└── conversion-report.json    # Detailed report
```

## 🎯 Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| Word   | `.docx`, `.doc` | Best with Pandoc installed |
| PDF    | `.pdf` | OCR for scanned PDFs |
| Excel  | `.xlsx`, `.xls` | Converts to Markdown tables |

## 🔧 Troubleshooting

### "Module not found" error?

Install missing dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

### Port 8000 already in use?

Edit `start_web_ui.py` and change `port=8000` to `port=8001`

### Python not found?

**Windows:** Download from https://www.python.org/downloads/  
**macOS:** `brew install python3`  
**Linux:** `sudo apt-get install python3 python3-pip`

### Files not converting?

Check the terminal for error messages. Common issues:
- File too large (>50MB limit)
- Unsupported file type
- Corrupted file

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Detailed startup guide
- **[WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)** - Complete user manual
- **[WEB_UI_IMPLEMENTATION.md](WEB_UI_IMPLEMENTATION.md)** - Technical details
- **[README.md](README.md)** - Full project documentation

## 🎨 Features

### Upload Section
- Drag-and-drop with visual feedback
- Multiple file support
- Real-time validation
- File type badges (DOCX=blue, PDF=red, XLSX=green)
- File size display

### Processing Section
- Animated spinner
- Progress bar (0-100%)
- Status updates every second

### Results Section
- Summary statistics
- Per-file quality scores
- Color-coded indicators (🟢 high, 🟡 medium, 🔴 low)
- Warnings and errors
- Download button

## 🔒 Security

- **File size limit:** 50MB per file
- **Local only:** Server binds to 127.0.0.1 (your computer only)
- **Auto cleanup:** Temporary files deleted after 60 seconds
- **No code execution:** Pure data processing

## 🚀 Advanced Usage

### Custom Port

```bash
# Edit start_web_ui.py, change:
port=8000  # to your preferred port
```

### External Access

```bash
# Edit start_web_ui.py, change:
host="127.0.0.1"  # to "0.0.0.0"
# ⚠️ Only on trusted networks!
```

### API Access

The web UI is built on a REST API you can use programmatically:

```python
import requests

# Upload files
files = [('files', open('document.docx', 'rb'))]
response = requests.post('http://localhost:8000/api/upload', files=files)
job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()

# Download results
result = requests.get(f'http://localhost:8000/api/download/{job_id}')
with open('results.zip', 'wb') as f:
    f.write(result.content)
```

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md#api-endpoints) for full API documentation.

## 🎓 Next Steps

1. ✅ Start the server
2. ✅ Convert some test documents
3. ✅ Review the conversion reports
4. ✅ Integrate into your workflow
5. 📖 Read the full [Web UI Guide](WEB_UI_GUIDE.md)

## 💡 Tips

- **Quality scores** help identify problematic conversions
- **Warnings** are informational (conversion still succeeded)
- **Errors** mean conversion failed for that file
- **Scanned PDFs** work best with Tesseract OCR installed
- **Large batches** (>20 files) may take a few minutes

## 🤝 Need Help?

1. Check [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed docs
2. Review [TROUBLESHOOTING](README.md#troubleshooting) section
3. Check the terminal output for error messages
4. Open an issue on GitHub

---

**Ready to start? Run `python start_web_ui.py` and open http://127.0.0.1:8000** 🎉

