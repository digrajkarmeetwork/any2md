# any2md

Convert any document (DOCX, PDF, XLSX) to Markdown with ease.

## Features

- 🪟 **Windows GUI App**: Easy-to-use desktop application (no installation required)
- 💻 **CLI Tool**: Command-line interface for developers
- 📄 **Multiple Formats**: DOCX, PDF, and Excel (XLSX) support
- 🖼️ **Smart Assets**: Automatic image extraction and organization
- 🔗 **Link Rewriting**: Automatic internal link conversion
- 🌐 **Cross-Platform**: Windows, macOS, and Linux

## Download

### Windows App (Recommended)

Download the standalone executable - no Python installation needed!

👉 **[Download any2md.exe](https://github.com/digrajkarmeetwork/any2md/releases/latest/download/any2md.exe)**

Just download and run - it's that simple!

### CLI Installation

```bash
pip install git+https://github.com/digrajkarmeetwork/any2md.git
```

## Usage

### Windows GUI App

1. Download `any2md.exe`
2. Double-click to run
3. Add your files (DOCX, PDF, Excel)
4. Choose output folder
5. Click Convert!

### CLI

```bash
# Convert a single file
any2md convert document.docx --out docs/

# Convert a directory
any2md convert ./source-docs --out docs/
```

## Building the Executable

To build the Windows executable yourself:

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller any2md.spec

# Find the executable in dist/any2md.exe
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Made with ❤️ by [Meet Digrajkar](https://github.com/digrajkarmeetwork)

