# OCR PDF Processor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/kobishahar/ocr-pdf-processor/ci.yml?branch=main)](https://github.com/kobishahar/ocr-pdf-processor/actions)

A Python wrapper around `ocrmypdf` for recursively processing PDF files with OCR capabilities. Supports Hebrew and English text recognition, batch processing, and configurable output options.

## Features

- Recursively scans for PDFs with include/exclude globs
- Builds and runs `ocrmypdf` with args from `ocr_config.json`
- Writes outputs to `OCR/<name>.ocr.pdf` next to each source PDF

## 📦 Installation

### Prerequisites

Ensure you have the following system dependencies installed:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ocrmypdf tesseract-ocr tesseract-ocr-heb poppler-utils

# macOS
brew install ocrmypdf tesseract tesseract-lang poppler

# Or using conda
conda install -c conda-forge ocrmypdf tesseract poppler
```

### From Source

```bash
# Clone the repository
git clone https://github.com/kobishahar/ocr-pdf-processor.git
cd ocr-pdf-processor

# Install in development mode
pip install -e .
```

### Using pip (when published)

```bash
pip install ocr-pdf-processor
```

## 🚀 Quick Start

### Command Line Usage

```bash
# Basic usage - process all PDFs in current directory (recursive)
python app.py

# Process a directory (outputs go to OCR subfolders next to each PDF)
python app.py /path/to/input

# Process a single file
python app.py /path/to/file.pdf
```

### Configuration File

Edit `ocr_config.json` (next to `app.py`):

```json
{
  "input_dir": "./pdfs",
  "include_glob": ["*.pdf"],
  "exclude_glob": ["OCR/**", "*/OCR/**"],
  "jobs": "auto",
  "overwrite": false,
  "timeout": 0,
  "ocrmypdf_args": ["-l", "heb+eng", "--skip-text", "--rotate-pages", "--deskew", "--clean"]
}
```

Then run:

```bash
python app.py --config ocr_config.json
```

## 🔧 Command Line Options

| Option               | Description                         | Default           |
| -------------------- | ----------------------------------- | ----------------- |
| `input`              | Directory or single PDF             | `input_dir`       |
| `--jobs`             | Parallel workers                    | Auto (CPU count)  |
| `--ocrmypdf-args`    | Args passed to `ocrmypdf`           | From config       |
| `--overwrite`        | Overwrite existing `*.ocr.pdf`      | False             |
| `--max-files`        | Limit processed files               | No limit          |

## 📚 Python API

```python
from ocr_pdf_processor import ocr_one
from pathlib import Path

# Process a single file (pass an argparse-like object with `ocrmypdf_args`, etc.)
pdf_path = Path("./document.pdf")
args = type("Args", (), {"ocrmypdf_args": ["-l", "heb+eng", "--skip-text"], "overwrite": False, "timeout": 0})()
result = ocr_one(pdf_path, args)
print(f"Status: {result.status}")
```

## 🏗️ Project Structure

```text
ocr-pdf-processor/
├── ocr_pdf_processor/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py          # Data models and types
│   │   ├── config_manager.py  # Configuration handling
│   │   └── ocr_processor.py   # OCR processing logic
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   ├── shell_utils.py     # Shell command utilities
│   └── cli/                   # Command-line interface
│       ├── __init__.py
│       └── main.py            # CLI entry point
├── tests/                     # Test suite
├── docs/                      # Documentation
├── pyproject.toml            # Project configuration
├── setup.py                  # Package setup (legacy)
└── README.md                 # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ocr_pdf_processor

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## 🔧 Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/kobishahar/ocr-pdf-processor.git
cd ocr-pdf-processor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black ocr_pdf_processor tests

# Lint code
flake8 ocr_pdf_processor tests

# Type checking
mypy ocr_pdf_processor

# All checks
pre-commit run --all-files
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **System Dependencies**:
  - `ocrmypdf`: PDF OCR processing
  - `tesseract`: OCR engine with Hebrew support
  - `poppler-utils`: PDF utilities (pdftotext, pdfinfo)
- **Operating System**: Linux, macOS, Windows (with appropriate dependencies)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Issue**: `ocrmypdf: command not found`

```bash
# Install system dependencies
sudo apt install ocrmypdf  # Ubuntu/Debian
brew install ocrmypdf      # macOS
```

**Issue**: Hebrew OCR not working

```bash
# Install Hebrew language data
sudo apt install tesseract-ocr-heb  # Ubuntu/Debian
brew install tesseract-lang         # macOS
```

**Issue**: Permission errors during in-place processing

```bash
# Ensure write permissions on PDF files
chmod +w *.pdf
```

### Getting Help

- 📧 Email: <kobi@example.com>
- 🐛 Issues: [GitHub Issues](https://github.com/kobishahar/ocr-pdf-processor/issues)
- 📖 Documentation: [Full Documentation](https://ocr-pdf-processor.readthedocs.io)

## 🙏 Acknowledgments

- [ocrmypdf](https://ocrmypdf.readthedocs.io/) - PDF OCR processing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Poppler](https://poppler.freedesktop.org/) - PDF utilities

## 📈 Roadmap

- [ ] Support for additional languages
- [ ] GUI interface
- [ ] Cloud storage integration
- [ ] Advanced OCR configuration options
- [ ] Performance optimizations
- [ ] Docker containerization
