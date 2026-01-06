"""
OCR processor module for OCR PDF processor.
Contains the main OCR processing logic for individual files.
"""
import shlex
import time
from pathlib import Path

from .models import OCRResult
from ..utils.shell_utils import run


def output_path_for(pdf_path: Path) -> Path:
    """Return `.../OCR/<stem>.ocr.pdf` next to the source file."""
    ocr_dir = pdf_path.parent / "OCR"
    stem = pdf_path.stem
    if stem.lower().endswith(".ocr"):
        stem = stem[:-4]
    return ocr_dir / f"{stem}.ocr.pdf"


def ocr_one(pdf_path: Path, args) -> OCRResult:
    """
    Process a single PDF file with OCR.
    
    Args:
        pdf_path: Path to the input PDF file
        args: Configuration arguments object
        
    Returns:
        OCRResult object with processing results
    """
    out_pdf = output_path_for(pdf_path)

    # overwrite logic
    if out_pdf.exists() and (not args.overwrite):
        return OCRResult(
            file=str(pdf_path),
            output=str(out_pdf),
            status="skipped_exists",
            note="",
        )

    # Ensure output directory exists
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    try:
        cmd = ["ocrmypdf", *list(args.ocrmypdf_args), str(pdf_path), str(out_pdf)]
        if getattr(args, "dry_run", False):
            print(f"CMD: {shlex.join(cmd)}")
            return OCRResult(file=str(pdf_path), output=str(out_pdf), status="dry_run", note="")

        print(f"CMD: {shlex.join(cmd)}")
        start = time.time()
        code, _stdout, stderr = run(
            cmd, timeout=args.timeout if args.timeout and args.timeout > 0 else None
        )
        elapsed = round(time.time() - start, 2)
        if code != 0:
            return OCRResult(
                file=str(pdf_path),
                output=str(out_pdf),
                status=f"error_{code}",
                note=stderr.strip()[:300],
                elapsed_sec=elapsed,
            )
        return OCRResult(
            file=str(pdf_path),
            output=str(out_pdf),
            status="ok",
            note="",
            elapsed_sec=elapsed,
        )

    except Exception as e:
        return OCRResult(file=str(pdf_path), output=str(out_pdf), status="error", note=str(e))
