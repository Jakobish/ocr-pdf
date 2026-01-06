"""
CLI interface module for OCR PDF processor.
Handles command line argument parsing and orchestrates the main execution flow.
"""
import argparse
import shlex
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pathlib import PurePosixPath
from typing import List

from ..core.config_manager import parse_config_path, load_config, build_defaults, listish
from ..core.ocr_processor import ocr_one


def create_parser(defaults: dict) -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    ap = argparse.ArgumentParser(
        description="Batch OCR for PDFs using ocrmypdf (outputs to ./OCR/*.ocr.pdf next to each source file)."
    )
    ap.add_argument(
        "--config",
        type=Path,
        help="JSON config file path (default: ocr_config.json next to app.py)",
    )
    ap.add_argument(
        "input",
        nargs="?",
        default=Path(defaults["input_dir"]),
        type=Path,
        help="A directory to scan recursively, or a single PDF file (default: input_dir from config).",
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
        "--jobs",
        type=int,
        default=defaults["jobs"],
        help="Parallel workers",
    )
    ap.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing `*.ocr.pdf` outputs",
    )
    ap.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="Do not overwrite existing outputs",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=defaults["timeout"],
        help="Per-file timeout (0=none)",
    )
    ap.add_argument(
        "--ocrmypdf-args",
        default=shlex.join(defaults["ocrmypdf_args"]),
        help="Arguments passed to `ocrmypdf` (excluding input/output paths).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running them",
    )
    ap.set_defaults(
        overwrite=defaults["overwrite"],
    )
    return ap


def scan_pdfs(args) -> List[Path]:
    """Scan input directory for PDF files based on include/exclude patterns."""
    if args.input.is_file():
        return [args.input]

    pdfs = []
    seen = set()
    for pattern in args.include_glob:
        for p in args.input_dir.rglob(pattern):
            if not p.is_file():
                continue
            # Avoid re-processing already OCR'd outputs, even if they leak into the scan.
            if p.name.lower().endswith(".ocr.pdf"):
                continue
            key = str(p)
            if key in seen:
                continue
            if args.exclude_glob:
                rel = PurePosixPath(p.relative_to(args.input_dir).as_posix())
                if any(rel.match(pat) for pat in args.exclude_glob):
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
        futs = {ex.submit(ocr_one, p, args): p for p in pdfs}
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            status = res.status
            file_path = res.file
            out_path = getattr(res, "output", "")
            note = res.note
            done = len(results)
            is_error = status.startswith("error")
            if report_every <= 0:
                if is_error:
                    print(f"[{status}] {file_path} -> {out_path} :: {note}")
            elif report_every == 1:
                print(f"[{status}] {file_path} -> {out_path} :: {note}")
            elif is_error or done % report_every == 0 or done == total:
                if is_error:
                    print(f"[{status}] {file_path} -> {out_path} :: {note}")
                else:
                    print(f"[{done}/{total}] {status} {file_path} -> {out_path} :: {note}")
    
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
    args.ocrmypdf_args = shlex.split(args.ocrmypdf_args)
    
    # Resolve paths
    args.input = args.input.expanduser().resolve()
    args.input_dir = args.input if args.input.is_dir() else args.input.parent
    args.input_dir = args.input_dir.expanduser().resolve()
    
    # Scan for PDFs
    pdfs = scan_pdfs(args)
    
    # Sort PDFs
    pdfs = sort_pdfs(pdfs, args.input_dir, args.sort_by)
    
    # Limit files
    if args.max_files > 0:
        pdfs = pdfs[: args.max_files]
    
    if not pdfs:
        print("No PDFs found under:", args.input_dir)
        sys.exit(1)
    
    # Start processing
    print(
        f"Found {len(pdfs)} PDFs. Starting… (jobs={args.jobs}, overwrite={args.overwrite})"
    )
    
    # Process files
    results = process_files(args, pdfs)
    ok = sum(1 for r in results if r.status == "ok")
    skipped = sum(1 for r in results if r.status == "skipped_exists")
    errors = len(results) - ok - skipped

    print(f"\nDone. ok={ok} skipped={skipped} errors={errors}")
    print("Outputs: OCR/*.ocr.pdf next to each source file")
