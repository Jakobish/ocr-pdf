# Debug Mode Specific Rules (Non-Obvious Only)

**System Dependency Errors**: Error code 127 specifically means "command not found" for system dependencies (ocrmypdf, tesseract, poppler-utils) - NOT Python library issues.

**macOS Timestamp Debug**: Creation time debugging requires `SetFile` and `GetFileInfo` commands. Check `pdf_utils.py` lines 177-211 for macOS-specific timestamp handling logic.

**Resume CSV Debugging**: Resume functionality silently fails if CSV contains relative paths. Debug by checking `models.py` line 106-108 where relative paths get resolved against input_dir.

**Text Detection Sampling**: Text layer detection samples only first N pages (default: 3) for performance. Debug duplicate detection in `pdf_utils.py` lines 54-55.

**Temporary File Debug**: OCR processing uses temporary file pattern with `.tmp_ocr` suffix for safe atomic replacement. Check `ocr_processor.py` lines 91-170 for the atomic replacement logic.

**Shell Command Debug**: All shell commands return (code, stdout, stderr) tuples. Error code 127 = command not found, 124 = timeout. See `shell_utils.py`.

**Config Loading Debug**: Config file defaults to `ocr_config.json` next to `app.py` NOT in project root. Debug path resolution in `config_manager.py` line 13.