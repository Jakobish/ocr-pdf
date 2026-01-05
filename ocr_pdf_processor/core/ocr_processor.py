"""
OCR processor module for OCR PDF processor.
Contains the main OCR processing logic for individual files.
"""
import time
from pathlib import Path

from .models import OCRResult
from ..utils.pdf_utils import has_text_layer, pdfinfo_dict, set_fs_times_from_xmp, copy_fs_times
from ..utils.shell_utils import run


def ocr_one(pdf_path: Path, out_dir: Path, args) -> OCRResult:
    """
    Process a single PDF file with OCR.
    
    Args:
        pdf_path: Path to the input PDF file
        out_dir: Output directory for processed files (ignored - we create .ocr.pdf next to source)
        args: Configuration arguments object
        
    Returns:
        OCRResult object with processing results
    """
    # Always create output file next to source with .ocr suffix
    out_pdf = pdf_path.parent / f"{pdf_path.stem}.ocr.pdf"

    # read metadata now (for timestamp preservation)
    meta = pdfinfo_dict(pdf_path)
    producer = meta.get("Producer", "")
    creation = (
        meta.get("CreationDate", "")
        or meta.get("Creation date", "")
        or meta.get("Creation Time", "")
    )
    moddate = (
        meta.get("ModDate", "") or meta.get("Mod date", "") or meta.get("Mod Time", "")
    )

    # detect text / duplication
    text_exists, dup_ratio, text_state = has_text_layer(
        pdf_path, sample_pages=args.text_sample_pages
    )

    # overwrite logic
    if out_pdf.exists() and (not args.overwrite):
        return OCRResult(
            file=str(pdf_path), 
            status="skipped_exists", 
            note="",
            producer=producer,
            creation=creation,
            moddate=moddate,
            dup_ratio=dup_ratio
        )

    # Ensure output directory exists
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    # Build ocrmypdf cmd
    base = [
        "ocrmypdf",
        "-l",
        args.lang,
        "--rotate-pages",
        "--optimize",
        str(args.optimize),
        "--jobs",
        str(args.ocr_jobs),
        "--output-type",
        "pdfa",
        "--skip-big",
        str(args.skip_big_mb),
    ]
    
    # redo policy
    redo = True
    if args.redo_policy == "aggressive":
        redo = True
    elif args.redo_policy == "auto":
        redo = text_exists and dup_ratio >= args.dup_threshold
    elif args.redo_policy == "never":
        redo = False

    # decide mode
    need_ocr = (not text_exists) or redo or args.force_ocr_all
    note = "copy"
    status = "copied_no_ocr"

    # write target safely (always create .ocr.pdf next to source)
    tmp_target = out_pdf
    if out_pdf.exists():
        tmp_target = Path(str(out_pdf) + ".tmp_ocr")

    try:
        if need_ocr:
            note = "redo" if (text_exists and (redo or args.force_ocr_all)) else "ocr"
            cmd = base[:]
            if text_exists and (redo or args.force_ocr_all):
                # For redo-ocr, avoid incompatible flags
                cmd.append("--redo-ocr")
                # Skip deskew and clean for redo-ocr compatibility
            else:
                # For fresh OCR, add the processing flags
                cmd.append("--skip-text")
                cmd.append("--deskew")
                cmd.append("--clean")
            if args.tesseract_time:
                cmd += ["--tesseract-timeout", str(args.tesseract_time)]
            if args.tesseract_pagesegmode:
                cmd += ["--tesseract-pagesegmode", str(args.tesseract_pagesegmode)]
            
            # Ensure proper file paths
            input_path = str(pdf_path)
            output_path = str(tmp_target)
            
            cmd += [input_path, output_path]
            start = time.time()
            code, out, err = run(
                cmd, timeout=args.timeout if args.timeout > 0 else None
            )
            elapsed = round(time.time() - start, 2)
            if code != 0:
                # Only show detailed debug info for usage errors (malformed commands)
                if 'usage:' in err and len(err) < 1000:
                    print("DEBUG: Command failed with usage message")
                    print(f"DEBUG: Full command: {' '.join(cmd)}")
                
                if tmp_target.exists():
                    try:
                        tmp_target.unlink()
                    except Exception as e:
                        print(f"How exceptional! {e}")
                        pass

                return OCRResult(
                    file=str(pdf_path),
                    status=f"error_{code}",
                    note=note + " :: " + err.strip()[:300],
                    producer=producer,
                    creation=creation,
                    moddate=moddate,
                    dup_ratio=dup_ratio,
                    elapsed_sec=elapsed,
                )
            status = "ok_ocr"
        else:
            # copy - create .ocr.pdf next to source
            try:
                tmp_target.write_bytes(pdf_path.read_bytes())
            except Exception:
                # fallback to cp command
                code, _, _ = run(["/bin/cp", str(pdf_path), str(tmp_target)])
                if code != 0:
                    return OCRResult(
                        file=str(pdf_path),
                        status="error_copy",
                        note="Failed to copy file",
                        producer=producer,
                        creation=creation,
                        moddate=moddate,
                        dup_ratio=dup_ratio,
                    )

        # if tmp target is temp, replace
        if tmp_target != out_pdf:
            # atomic-ish replace
            if out_pdf.exists():
                out_pdf.unlink()
            tmp_target.replace(out_pdf)

        # preserve file timestamps
        if args.preserve_fstimes == "xmp":
            if creation or moddate:
                set_fs_times_from_xmp(out_pdf, creation, moddate)
        elif args.preserve_fstimes == "fs":
            copy_fs_times(pdf_path, out_pdf)

        return OCRResult(
            file=str(pdf_path),
            status=status,
            note=note,
            producer=producer,
            creation=creation,
            moddate=moddate,
            dup_ratio=dup_ratio,
        )

    except Exception as e:
        # cleanup tmp
        if tmp_target != out_pdf and tmp_target.exists():
            try:
                tmp_target.unlink()
            except Exception as e:
                print(f"How exceptional! {e}")
                pass
        return OCRResult(file=str(pdf_path), status="error", note=str(e))