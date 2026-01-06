"""
OCR PDF Processor Package

A thin wrapper around `ocrmypdf` for recursively OCR'ing PDFs.
"""

__version__ = "1.0.0"
__author__ = "Kobi Shahar"
__email__ = "kobi@example.com"
__description__ = "Batch OCR for PDFs with Hebrew and English support"

from .core.config_manager import parse_config_path, load_config, build_defaults
from .core.ocr_processor import ocr_one, output_path_for
from .core.models import OCRResult
from .utils.shell_utils import run, have

__all__ = [
    "OCRResult",
    "ocr_one",
    "output_path_for",
    "run",
    "have",
    "parse_config_path",
    "load_config",
    "build_defaults",
]
