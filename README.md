# OCR PDF Processor

[![Python 3.8+] (https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status] (https://img.shields.io/badge/build-passing-brightgreen.svg)] (<https://github.com/kobishahar/ocr-pdf-processor/actions>)
()

A robust Python package for batch OCR processing of PDF files with support for Hebrew and English text. Built with production-ready architecture and modern Python best practices.

## 🌟 Features

- **Multi-language Support**: Hebrew and English OCR using Tesseract
- **Batch Processing**: Process hundreds of PDFs efficiently with parallel execution
- **Smart Text Detection**: Automatically detects existing text layers and duplicates
- **In-place Processing**: Safe in-place processing with temporary file backup
- **Metadata Preservation**: Maintains original file timestamps and metadata
- **Flexible Configuration**: JSON configuration files and command-line options
- **Comprehensive Reporting**: CSV reports for processing results
- **Resume Capability**: Resume interrupted processing from CSV reports
- **Production Ready**: Modular architecture, proper error handling, logging

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
# Basic usage - process all PDFs in current directory
python app.py

# Process specific directory
python app.py /path/to/input /path/to/output

# In-place processing (recommended for safety)
python app.py --in-place --preserve-fstimes xmp

# Force OCR on all files
python app.py --force-ocr-all

# Resume from previous run
python app.py --resume-from-csv --csv-append
```

### Configuration File

Create a `ocr_config.json` file:

```json
{
  "input_dir": "./pdfs",
  "output_dir": "./output",
  "include_glob": ["*.pdf"],
  "exclude_glob": ["*_processed.pdf"],
  "lang": "heb+eng",
  "optimize": 1,
  "jobs": 4,
  "preserve_fstimes": "xmp",
  "csv": "ocr_report.csv"
}
```

Then run:

```bash
python app.py --config ocr_config.json
```

## 🔧 Command Line Options

| Option               | Description                         | Default           |
| -------------------- | ----------------------------------- | ----------------- |
| `input_dir`          | Source directory for PDFs           | Current directory |
| `output_dir`         | Output directory                    | `./out_pdfs`      |
| `--lang`             | Tesseract languages                 | `heb+eng`         |
| `--jobs`             | Parallel workers                    | Auto (CPU count)  |
| `--optimize`         | PDF optimization level (0-3)        | 1                 |
| `--in-place`         | Process files in place              | False             |
| `--preserve-fstimes` | Preserve timestamps (xmp/fs/none)   | xmp               |
| `--resume-from-csv`  | Skip processed files                | False             |
| `--force-ocr-all`    | Force OCR on all files              | False             |
| `--redo-policy`      | Redo policy (auto/aggressive/never) | auto              |
| `--max-files`        | Limit processed files               | No limit          |

## 📚 Python API

```python
from ocr_pdf_processor import OCRConfig, ocr_one, CSVReporter
from pathlib import Path

# Create configuration
config = OCRConfig(
    input_dir=Path("./pdfs"),
    output_dir=Path("./output"),
    lang="heb+eng",
    optimize=1,
    jobs=4,
    # ... other options
)

# Process single file
pdf_path = Path("./document.pdf")
result = ocr_one(pdf_path, config.output_dir, config)
print(f"Status: {result.status}")

# Generate CSV report
reporter = CSVReporter(Path("report.csv"))
reporter.write_results([result])
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
│   │   └── pdf_utils.py       # PDF processing utilities
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
