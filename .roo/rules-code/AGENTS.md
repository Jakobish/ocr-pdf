# Code Mode Specific Rules (Non-Obvious Only)

**Output File Strategy**: Files are ALWAYS created with `.ocr.pdf` suffix next to source files, regardless of `output_dir` parameter. The `output_dir` parameter is effectively ignored.

**Config File Resolution**: Configuration is loaded from `ocr_config.json` next to `app.py`, NOT from project root. Default path is hardcoded as `Path(__file__).resolve().parent / "ocr_config.json"`.

**Type Conversion System**: Complex type conversion helpers in `config_manager.py` handle string/bool/int/float/list conversions with fallback defaults. Use these instead of manual conversions.

**macOS Timestamp Handling**: Special `SetFile` command integration in `pdf_utils.py` for macOS creation time preservation. Uses `GetFileInfo` + `SetFile -d` for copying creation times.

**Test File Organization**: Pytest requires test files in same directory as source files for discovery - NOT in separate tests/ folder structure.

**Atomic File Replacement**: Uses temporary file + replace pattern for safe file operations. Check `ocr_processor.py` lines 166-170 for the pattern.

**Shell Command Error 127**: Specifically indicates "command not found" for system dependencies (ocrmypdf, tesseract, poppler-utils).

**Dual Job Configuration**: Separate `--jobs` (Python threading) vs `--ocr-jobs` (ocrmypdf internal parallelism) parameters with different defaults.