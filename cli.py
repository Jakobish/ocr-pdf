"""
CLI interface module for OCR PDF processor.
Handles command line argument parsing and orchestrates the main execution flow.
"""
import argparse
import fnmatch
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from config_manager import parse_config_path, load_config, build_defaults, listish
from models import CSVReporter
from ocr_processor import ocr_one


def create_parser(defaults: dict) -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    ap = argparse.ArgumentParser(
        description="Batch OCR for PDFs (heb+eng) with safe in-place/outputs and FS time preservation."
    )
    ap.add_argument(
        "--config",
        type=Path,
        help="JSON config file path (default: ocr_config.json next to app.py)",
    )
    ap.add_argument(
        "input_dir",
        nargs="?",
        default=Path(defaults["input_dir"]),
        type=Path,
        help="Source directory (default: current dir)",
    )
    ap.add_argument(
        "output_dir",
        nargs="?",
        default=Path(defaults["output_dir"]),
        type=Path,
        help="Destination directory (default: ./out_pdfs). Ignored if --in-place",
    )
    ap.add_argument(
        "--include-glob",
        default=",".join(defaults["include_glob"]),
        help="Comma-separated glob(s) to include, relative to input_dir",
    )
    ap.add_argument(
        "--exclude-glob",
        default=",".join(defaults["exclude_glob"]),
        help="Comma-separated glob(s) to exclude, relative to input_dir",
    )
    ap.add_argument(
        "--exclude-output-dir",
        dest="exclude_output_dir",
        action="store_true",
        help="Skip output_dir when it is under input_dir",
    )
    ap.add_argument(
        "--no-exclude-output-dir",
        dest="exclude_output_dir",
        action="store_false",
        help="Do not skip output_dir during scanning",
    )
    ap.add_argument(
        "--sort-by",
        choices=["none", "path", "mtime", "size"],
        default=defaults["sort_by"],
        help="Sort order for inputs (default: none)",
    )
    ap.add_argument(
        "--max-files",
        type=int,
        default=defaults["max_files"],
        help="Limit number of files processed (0 = no limit)",
    )
    ap.add_argument(
        "--print-every",
        type=int,
        default=defaults["print_every"],
        help="Print progress every N files (1 = every file, 0 = errors only)",
    )
    ap.add_argument(
        "--lang",
        default=defaults["lang"],
        help="Tesseract languages (default: heb+eng)",
    )
    ap.add_argument(
        "--optimize",
        type=int,
        default=defaults["optimize"],
        help="ocrmypdf --optimize (0-3). Default 1",
    )
    ap.add_argument(
        "--skip-big-mb",
        type=int,
        default=defaults["skip_big_mb"],
        help="Skip files larger than X MB (default 2048)",
    )
    ap.add_argument(
        "--jobs",
        type=int,
        default=defaults["jobs"],
        help="Parallel workers",
    )
    ap.add_argument(
        "--ocr-jobs",
        type=int,
        default=defaults["ocr_jobs"],
        help="--jobs inside ocrmypdf per file",
    )
    ap.add_argument(
        "--redo-policy",
        choices=["auto", "aggressive", "never"],
        default=defaults["redo_policy"],
        help="auto=redo on suspected duplication; aggressive=redo for all; never=never redo",
    )
    ap.add_argument(
        "--dup-threshold",
        type=float,
        default=defaults["dup_threshold"],
        help="Duplicate-line ratio for redo (default 0.15)",
    )
    ap.add_argument(
        "--text-sample-pages",
        type=int,
        default=defaults["text_sample_pages"],
        help="Pages to sample for text detection (default 3)",
    )
    ap.add_argument(
        "--force-ocr-all",
        dest="force_ocr_all",
        action="store_true",
        help="Force OCR even if text exists (not recommended generally)",
    )
    ap.add_argument(
        "--no-force-ocr-all",
        dest="force_ocr_all",
        action="store_false",
        help="Disable forced OCR even if text exists",
    )
    ap.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing outputs",
    )
    ap.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="Do not overwrite existing outputs",
    )
    ap.add_argument(
        "--in-place",
        dest="in_place",
        action="store_true",
        help="Process and replace PDFs in place (safe temp+replace)",
    )
    ap.add_argument(
        "--no-in-place",
        dest="in_place",
        action="store_false",
        help="Write outputs to output_dir (no in-place)",
    )
    ap.add_argument(
        "--preserve-fstimes",
        choices=["xmp", "fs", "none"],
        default=defaults["preserve_fstimes"],
        help="Preserve output file times from: xmp (default), fs (source file), none",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=defaults["timeout"],
        help="Per-file timeout (0=none)",
    )
    ap.add_argument(
        "--tesseract-time",
        type=int,
        default=defaults["tesseract_time"],
        help="--tesseract-timeout seconds",
    )
    ap.add_argument(
        "--tesseract-pagesegmode",
        type=int,
        default=defaults["tesseract_pagesegmode"],
        help="--tesseract-pagesegmode (0=auto)",
    )
    ap.add_argument(
        "--resume-from-csv",
        dest="resume_from_csv",
        action="store_true",
        help="Skip files already listed in the CSV report",
    )
    ap.add_argument(
        "--no-resume-from-csv",
        dest="resume_from_csv",
        action="store_false",
        help="Do not skip files based on the CSV report",
    )
    ap.add_argument(
        "--csv-append",
        dest="csv_append",
        action="store_true",
        help="Append to existing CSV instead of overwriting",
    )
    ap.add_argument(
        "--no-csv-append",
        dest="csv_append",
        action="store_false",
        help="Overwrite CSV instead of append",
    )
    ap.add_argument(
        "--csv",
        type=Path,
        default=Path(defaults["csv"]),
        help="CSV report path",
    )
    ap.set_defaults(
        force_ocr_all=defaults["force_ocr_all"],
        overwrite=defaults["overwrite"],
        in_place=defaults["in_place"],
        exclude_output_dir=defaults["exclude_output_dir"],
        resume_from_csv=defaults["resume_from_csv"],
        csv_append=defaults["csv_append"],
    )
    return ap


def scan_pdfs(args) -> List[Path]:
    """Scan input directory for PDF files based on include/exclude patterns."""
    pdfs = []
    seen = set()
    for pattern in args.include_glob:
        for p in args.input_dir.rglob(pattern):
            if not p.is_file():
                continue
            key = str(p)
            if key in seen:
                continue
            if args.exclude_glob:
                rel = p.relative_to(args.input_dir).as_posix()
                if any(fnmatch.fnmatch(rel, pat) for pat in args.exclude_glob):
                    continue
            seen.add(key)
            pdfs.append(p)
    return pdfs


def sort_pdfs(pdfs: List[Path], input_dir: Path, sort_by: str) -> List[Path]:
    """Sort PDF list based on specified criteria."""
    if sort_by == "path":
        pdfs.sort(key=lambda p: p.relative_to(input_dir).as_posix().lower())
    elif sort_by == "mtime":
        pdfs.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0)
    elif sort_by == "size":
        pdfs.sort(key=lambda p: p.stat().st_size if p.exists() else 0)
    return pdfs


def process_files(args, pdfs: List[Path]) -> List:
    """Process PDF files using thread pool executor."""
    results = []
    total = len(pdfs)
    report_every = args.print_every
    
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(ocr_one, p, args.output_dir, args): p for p in pdfs}
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            status = res.status
            file_path = res.file
            note = res.note
            done = len(results)
            is_error = status.startswith("error")
            if report_every <= 0:
                if is_error:
                    print(f"[{status}] {file_path} :: {note}")
            elif report_every == 1:
                print(f"[{status}] {file_path} :: {note}")
            elif is_error or done % report_every == 0 or done == total:
                if is_error:
                    print(f"[{status}] {file_path} :: {note}")
                else:
                    print(f"[{done}/{total}] {status} {file_path} :: {note}")
    
    return results


def main():
    """Main CLI entry point."""
    # Parse config path first
    config_path, config_required = parse_config_path(sys.argv[1:])
    
    # Load configuration
    config = load_config(config_path, config_required)
    defaults = build_defaults(config)
    
    # Create parser
    ap = create_parser(defaults)
    
    # Set config default before parsing
    ap.set_defaults(config=config_path)
    
    # Parse arguments
    args = ap.parse_args()
    
    # Post-process arguments
    args.include_glob = listish(args.include_glob, defaults["include_glob"])
    args.exclude_glob = listish(args.exclude_glob, defaults["exclude_glob"])
    if args.max_files < 0:
        args.max_files = 0
    if args.print_every < 0:
        args.print_every = defaults["print_every"]
    if args.text_sample_pages < 1:
        args.text_sample_pages = defaults["text_sample_pages"]
    args.csv = args.csv.expanduser()
    
    # Resolve paths
    args.input_dir = args.input_dir.expanduser().resolve()
    if not args.in_place:
        args.output_dir = args.output_dir.expanduser().resolve()
        args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle output directory exclusion
    exclude_globs = list(args.exclude_glob)
    if args.exclude_output_dir and not args.in_place:
        try:
            rel_out = args.output_dir.relative_to(args.input_dir)
        except ValueError:
            rel_out = None
        if rel_out and rel_out.as_posix() not in (".", ""):
            exclude_globs.append((rel_out / "**").as_posix())
    args.exclude_glob = exclude_globs
    
    # Scan for PDFs
    pdfs = scan_pdfs(args)
    
    # Resume from CSV if requested
    if args.resume_from_csv:
        csv_reporter = CSVReporter(args.csv)
        processed = csv_reporter.load_processed(args.input_dir)
        if processed:
            pdfs = [p for p in pdfs if str(p) not in processed]
    
    # Sort PDFs
    pdfs = sort_pdfs(pdfs, args.input_dir, args.sort_by)
    
    # Limit files
    if args.max_files > 0:
        pdfs = pdfs[: args.max_files]
    
    if not pdfs:
        print("No PDFs found under:", args.input_dir)
        sys.exit(1)
    
    # Warnings
    if args.resume_from_csv and args.csv.exists() and not args.csv_append:
        print(
            "Warning: resume_from_csv is enabled but csv_append is false; CSV will be overwritten.",
            file=sys.stderr,
        )
    
    # Start processing
    print(
        f"Found {len(pdfs)} PDFs. Starting… (in_place={args.in_place}, preserve_fstimes={args.preserve_fstimes})"
    )
    
    # Process files
    results = process_files(args, pdfs)
    
    # Write CSV report
    csv_reporter = CSVReporter(args.csv)
    csv_reporter.write_results(results, args.csv_append)
    
    print("\nDone. Report:", args.csv)
    if not args.in_place:
        print("Output dir:", args.output_dir)