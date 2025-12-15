# Contributing to doc2mkdocs

Thank you for your interest in contributing to doc2mkdocs! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/doc2mkdocs.git
cd doc2mkdocs
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**

```bash
pip install -e ".[dev]"
```

4. **Install system dependencies**

For full functionality, install Tesseract and Pandoc (see README.md).

## Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking

Before submitting a PR, run:

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type check
mypy src/
```

## Testing

All new features should include tests. Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/doc2mkdocs --cov-report=html
```

Aim for >80% code coverage for new code.

## Adding a New Converter

To add support for a new file format:

1. **Create a new converter class** in `src/doc2mkdocs/converters/`

```python
from doc2mkdocs.core.base_converter import BaseConverter, ConversionResult

class MyFormatConverter(BaseConverter):
    @property
    def supported_extensions(self) -> list[str]:
        return [".myformat"]
    
    def can_convert(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions
    
    def convert(self, file_path: Path) -> ConversionResult:
        # Implement conversion logic
        pass
```

2. **Register the converter** in `src/doc2mkdocs/converters/__init__.py`

3. **Add the converter** to the CLI in `src/doc2mkdocs/cli.py`

4. **Write tests** in `tests/test_converters.py`

## Pull Request Process

1. Create a new branch for your feature/fix
2. Make your changes with clear, descriptive commits
3. Add/update tests as needed
4. Update documentation (README, CHANGELOG)
5. Ensure all tests pass and code is formatted
6. Submit a pull request with a clear description

## Commit Messages

Use clear, descriptive commit messages:

- `feat: Add PPTX converter`
- `fix: Handle empty Excel sheets`
- `docs: Update installation instructions`
- `test: Add tests for link rewriting`

## Questions?

Feel free to open an issue for questions or discussions!

