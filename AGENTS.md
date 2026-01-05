# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Project-Specific Rules

**System Dependencies Required**: Must have `ocrmypdf`, `tesseract-ocr-heb`, and `poppler-utils` installed system-wide - these are NOT Python dependencies.

**Output File Naming**: Always creates `.ocr.pdf` files next to source files, NOT in output directory (output_dir parameter is ignored).

**Config File Location**: Looks for `ocr_config.json` next to `app.py`, NOT in project root.

**Default Languages**: Uses Hebrew+English (`heb+eng`) as default OCR languages.

**Test File Placement**: Test files MUST be in same directory as source files for pytest to work - NOT in separate tests/ folder.

**macOS Timestamps**: Uses `SetFile` command for creation time preservation on macOS (requires macOS-specific setup).

**Resume CSV Handling**: Resume functionality expects absolute paths in CSV - relative paths get resolved against input_dir.

**Duplicate Detection**: Intelligent redo policy samples only first N pages (default: 3) for text detection, not entire file.

**Error Code 127**: Specifically means "command not found" for system dependencies.

**Job Separation**: Has separate job counts: `--jobs` (threading) vs `--ocr-jobs` (ocrmypdf internal parallelism).