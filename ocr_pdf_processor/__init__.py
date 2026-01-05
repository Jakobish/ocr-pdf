"""
OCR PDF Processor Package

A robust Python package for batch OCR processing of PDF files with support for Hebrew and English text.
"""

__version__ = "1.0.0"
__author__ = "Kobi Shahar"
__email__ = "kobi@example.com"
__description__ = "Batch OCR for PDFs with Hebrew and English support"

from .core.config_manager import parse_config_path, load_config, build_defaults
from .core.ocr_processor import ocr_one
from .core.models import OCRConfig, OCRResult, PDFMetadata, CSVReporter
from .utils.shell_utils import run, have
from .utils.pdf_utils import (
    has_text_layer, 
    pdfinfo_dict, 
    parse_xmp_date, 
    set_fs_times_from_xmp, 
    copy_fs_times
)

__all__ = [
    "OCRConfig",
    "OCRResult", 
    "PDFMetadata",
    "CSVReporter",
    "ocr_one",
    "run",
    "have",
    "has_text_layer",
    "pdfinfo_dict",
    "parse_xmp_date",
    "set_fs_times_from_xmp",
    "copy_fs_times",
    "parse_config_path",
    "load_config",
    "build_defaults",
]