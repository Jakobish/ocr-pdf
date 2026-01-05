# Architect Mode Specific Rules (Non-Obvious Only)

**Dual Entry Point Architecture**: Project supports both library API (functions in `ocr_pdf_processor.core.ocr_processor`) and CLI interface (`python app.py`), but CLI ignores output_dir parameter entirely.

**Config Resolution Pattern**: Default config path is resolved relative to `__file__` location, not project root. See `config_manager.py` line 13 for the hardcoded path resolution pattern.

**Atomic File Operations**: File replacement uses temporary file + atomic replace pattern for safety. See `ocr_processor.py` lines 166-170 for the exact implementation.

**macOS-Specific Dependencies**: Timestamp preservation requires `SetFile` and `GetFileInfo` commands on macOS, creating platform-specific behavior. See `pdf_utils.py` lines 177-211.

**Text Detection Optimization**: PDF text detection samples only first N pages (configurable, default 3) rather than processing entire file for performance.

**Job Separation Design**: Architecture separates Python threading (`--jobs`) from ocrmypdf internal parallelism (`--ocr-jobs`) with different auto-calculation defaults.

**Resume CSV Absolute Path Requirement**: CSV resume functionality requires absolute file paths in CSV records, with relative path resolution against input_dir at load time.