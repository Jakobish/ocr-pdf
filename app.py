#!/usr/bin/env python3
"""
OCR PDF Processor - Main Entry Point

A robust Python package for batch OCR processing of PDF files with support for Hebrew and English text.
"""

import sys
from ocr_pdf_processor.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
