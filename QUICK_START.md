# Quick Start - Web UI

## Step 1: Install Dependencies

First, make sure you have Python 3.11+ installed. Then install the required dependencies:

```bash
pip install fastapi uvicorn python-multipart
```

Or install all dependencies for the full package:

```bash
pip install -e ".[web]"
```

## Step 2: Start the Server

### Option A: Using the startup script (Easiest)

**Windows:**
```bash
# Double-click start_web_ui.bat
# Or run in terminal:
start_web_ui.bat
```

**macOS/Linux:**
```bash
python3 start_web_ui.py
```

### Option B: Using the CLI (After installation)

```bash
doc2mkdocs serve
```

### Option C: Direct Python execution

```bash
python3 -c "from src.doc2mkdocs.web import create_app; import uvicorn; uvicorn.run(create_app(), host='127.0.0.1', port=8000)"
```

## Step 3: Open Your Browser

Navigate to: **http://127.0.0.1:8000**

You should see the doc2mkdocs web interface!

## Step 4: Convert Documents

1. **Drag and drop** files onto the upload area (or click to browse)
2. Wait for files to be **validated** (green checkmark = valid)
3. Click **"Convert Files"** button
4. Watch the **progress bar** as files are converted
5. Review the **conversion report** with quality scores
6. Click **"Download ZIP"** to get your converted files

## What You'll Get

The downloaded ZIP file contains:
- ✅ Converted Markdown files (`.md`)
- ✅ Extracted images in `assets/` folder
- ✅ `conversion-report.json` with detailed results

## Troubleshooting

### "Module not found" errors

Install dependencies:
```bash
pip install fastapi uvicorn python-multipart mammoth pymupdf openpyxl pyyaml typer rich
```

### "Address already in use"

Another service is using port 8000. Try a different port:
```bash
# Edit start_web_ui.py and change port=8000 to port=8001
# Or use the CLI:
doc2mkdocs serve --port 8001
```

### Python not found

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3 python3-pip
```

## Next Steps

- Read the full [Web UI Guide](WEB_UI_GUIDE.md)
- Check out the [API documentation](WEB_UI_GUIDE.md#api-endpoints)
- See the [visual demo](docs-example/web-ui-demo.md)

## Need Help?

- Check [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed documentation
- Review [TROUBLESHOOTING.md](README.md#troubleshooting) for common issues
- Open an issue on GitHub

---

**Enjoy converting your documents! 🚀**

