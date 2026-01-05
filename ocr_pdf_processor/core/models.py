"""
Data models and configuration structures for the OCR PDF processor.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv


@dataclass
class OCRConfig:
    """Configuration class for OCR processing settings."""
    input_dir: Path
    output_dir: Path
    include_glob: List[str]
    exclude_glob: List[str]
    exclude_output_dir: bool
    sort_by: str
    max_files: int
    print_every: int
    lang: str
    optimize: int
    skip_big_mb: int
    jobs: int
    ocr_jobs: int
    redo_policy: str
    dup_threshold: float
    force_ocr_all: bool
    overwrite: bool
    in_place: bool
    resume_from_csv: bool
    csv_append: bool
    preserve_fstimes: str
    timeout: int
    text_sample_pages: int
    tesseract_time: int
    tesseract_pagesegmode: int
    csv: Path


@dataclass
class OCRResult:
    """Result class for OCR processing of a single file."""
    file: str
    status: str
    note: str
    producer: str = ""
    creation: str = ""
    moddate: str = ""
    dup_ratio: float = 0.0
    elapsed_sec: float = 0.0


@dataclass
class PDFMetadata:
    """PDF metadata container."""
    producer: str
    creation: str
    moddate: str


class CSVReporter:
    """Handles CSV reporting functionality."""
    
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.headers = ["file", "status", "note", "producer", "creation", "moddate", "dup_ratio"]
    
    def write_results(self, results: List[OCRResult], append: bool = False):
        """Write OCR results to CSV file."""
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        csv_mode = "a" if append else "w"
        write_header = True
        
        if append and self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            write_header = False
        
        with open(self.csv_path, csv_mode, newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.headers)
            if write_header:
                writer.writeheader()
            
            for result in results:
                row = {
                    "file": result.file,
                    "status": result.status,
                    "note": result.note,
                    "producer": result.producer,
                    "creation": result.creation,
                    "moddate": result.moddate,
                    "dup_ratio": result.dup_ratio,
                }
                writer.writerow(row)
    
    def load_processed(self, input_dir: Path) -> set:
        """Load previously processed files from CSV for resume functionality."""
        processed = set()
        try:
            with self.csv_path.open("r", newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    file_path = row.get("file")
                    if not file_path:
                        continue
                    p = Path(file_path)
                    if not p.is_absolute():
                        p = (input_dir / p).resolve()
                    processed.add(str(p))
        except FileNotFoundError:
            return processed
        except Exception as e:
            print(f"Warning: failed to read resume CSV: {self.csv_path} ({e})", file=__import__('sys').stderr)
        return processed