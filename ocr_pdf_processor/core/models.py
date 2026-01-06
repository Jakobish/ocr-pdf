"""
Data models and configuration structures for the OCR PDF processor.
"""
from dataclasses import dataclass

@dataclass
class OCRResult:
    """Result class for OCR processing of a single file."""
    file: str
    output: str
    status: str
    note: str
    elapsed_sec: float = 0.0
