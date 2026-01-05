# Ask Mode Specific Rules (Non-Obvious Only)

**Configuration File Location**: The main config file `ocr_config.json` is located next to `app.py` (in project root), NOT in the `ocr_pdf_processor` package directory. Default path is hardcoded as `Path(__file__).resolve().parent / "ocr_config.json"`.

**Command Entry Point**: CLI interface is in `ocr_pdf_processor.cli.main:main` function, but command-line usage shows `python app.py` (not the package CLI). The package provides both CLI and library interfaces.

**Hidden Configuration Structure**: Configuration supports nested `{"value": "..."}` objects in JSON config files. See `config_manager.py` lines 85-89 for the unwrap logic.

**File Output Location**: Despite having `output_dir` parameter, processed files are ALWAYS created next to source files with `.ocr.pdf` suffix. The output_dir parameter is effectively ignored.

**Language Default**: Uses Hebrew+English (`heb+eng`) as default OCR languages, not English-only.

**System vs Python Dependencies**: External tools (`ocrmypdf`, `tesseract-ocr-heb`, `poppler-utils`) must be installed at system level, not via pip.