# Quick Start Guide

Get up and running with doc2mkdocs in 5 minutes.

## Step 1: Install

```bash
pip install .
```

## Step 2: Prepare Your Documents

Organize your source documents in a folder:

```
my-docs/
├── guide.docx
├── manual.pdf
└── data.xlsx
```

## Step 3: Convert

```bash
doc2mkdocs convert my-docs/ --out docs/
```

## Step 4: Review Output

Check the generated files:

```
docs/
├── assets/
│   ├── guide/
│   ├── manual/
│   └── data/
├── guide.md
├── manual.md
├── data.md
└── conversion-report.json
```

## Step 5: Set Up MkDocs (Optional)

If you want to build a documentation site:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Copy sample config
cp docs-example/mkdocs.yml .

# Edit mkdocs.yml and add your navigation structure
# You can use the generated mkdocs-nav-snippet.yml as a starting point

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Common Workflows

### Convert Single File

```bash
doc2mkdocs convert report.docx --out docs/
```

### Convert with OCR for Scanned PDFs

```bash
doc2mkdocs convert scanned.pdf --out docs/ --pdf-ocr on
```

### Convert Excel with All Sheets in One File

```bash
doc2mkdocs convert data.xlsx --out docs/ --excel-mode single-page
```

### Generate MkDocs Navigation

```bash
doc2mkdocs convert my-docs/ --out docs/ --mkdocs-nav
# Then copy content from docs/mkdocs-nav-snippet.yml to your mkdocs.yml
```

### Overwrite Existing Files

```bash
doc2mkdocs convert my-docs/ --out docs/ --overwrite
```

## Next Steps

- Read the full [README.md](README.md) for all options
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to add new features
- Review the conversion report to identify quality issues
- Customize the generated Markdown as needed
- Set up MkDocs for a beautiful documentation site

## Tips

1. **Always review the conversion report** - It highlights warnings and quality scores
2. **Use Pandoc for best DOCX quality** - Install it for better conversion results
3. **Enable OCR only when needed** - It's slower but necessary for scanned PDFs
4. **Organize source docs in folders** - The tool preserves directory structure
5. **Check image paths** - Ensure images are correctly referenced in your MkDocs config

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the conversion report for specific file issues
- Open an issue on GitHub for bugs or feature requests

