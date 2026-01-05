"""
PDF utilities module for OCR PDF processor.
Provides functions for PDF text detection, metadata extraction, and file timestamp management.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Optional

from .shell_utils import run, have


# XMP date formats commonly: "D:YYYYMMDDHHmmSS[Z|+hh'mm']" or ISO-like
_XMP_RE = re.compile(
    r"(?:D:)?(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?(Z|[+\-]\d{2}'?\d{2})?"
)


def has_text_layer(pdf_path: Path, sample_pages: int = 3) -> Tuple[bool, float, str]:
    """
    Check if a PDF has text layer content using pdftotext.
    
    Args:
        pdf_path: Path to the PDF file
        sample_pages: Number of pages to sample for text detection
        
    Returns:
        Tuple of (has_text, duplicate_ratio, status_message)
    """
    # uses poppler 'pdftotext'
    cmd = [
        "pdftotext",
        "-f",
        "1",
        "-l",
        str(sample_pages),
        "-enc",
        "UTF-8",
        "-q",
        str(pdf_path),
        "-",
    ]
    code, out, _ = run(cmd, timeout=60)
    if code != 0:
        return False, 0.0, "pdftotext_failed"
    text = out.strip()
    if not text:
        return False, 0.0, "empty"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return True, 0.0, "has_text"
    dup_lines = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i - 1])
    dup_ratio = dup_lines / max(1, len(lines))
    return True, dup_ratio, "has_text"


def pdfinfo_dict(pdf_path: Path) -> Dict[str, str]:
    """
    Extract PDF metadata using pdfinfo.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary of metadata key-value pairs
    """
    # try json
    code, out, _ = run(["pdfinfo", "-json", str(pdf_path)], timeout=30)
    if code == 0 and out.strip().startswith("{"):
        # minimal parse to dict (avoid json import if not present)
        # but we need Producer/CreationDate/ModDate: use plain parsing fallback for reliability
        pass
    code, out, _ = run(["pdfinfo", str(pdf_path)], timeout=30)
    meta = {}
    if code == 0:
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def parse_xmp_date(s: str) -> Optional[datetime]:
    """
    Parse XMP date string to datetime object.
    
    Args:
        s: XMP date string
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not s:
        return None
    s = s.strip()
    m = _XMP_RE.match(s)
    if not m:
        # try loose ISO and other common formats
        # First try to handle timezone abbreviations by removing them
        tz_removed = s
        for tz in ['IDT', 'UTC', 'GMT', 'EST', 'EDT', 'CST', 'CDT', 'MST', 'MDT', 'PST', 'PDT']:
            if s.endswith(' ' + tz):
                tz_removed = s[:-len(' ' + tz)]
                break
        
        formats_to_try = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d", 
            "%d/%m/%Y", 
            "%m/%d/%Y",
            "%a %b %d %H:%M:%S %Y",    # without timezone
            "%a %b %d %H:%M:%S %Y %z", # with numeric timezone
        ]
        
        # Try with timezone removed first
        for fmt in formats_to_try:
            try:
                return datetime.strptime(tz_removed, fmt)
            except Exception:
                pass
                
        # Try original string with timezone format as fallback
        formats_with_tz = [
            "%a %b %d %H:%M:%S %Y %Z",  # e.g., "Mon Jul 17 17:26:13 2023 IDT"
        ]
        
        for fmt in formats_with_tz:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        for fmt in formats_to_try:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        return None
    y, mo, d, hh, mm, ss, tz = m.groups()
    y = int(y)
    mo = int(mo or 1)
    d = int(d or 1)
    hh = int(hh or 0)
    mm = int(mm or 0)
    ss = int(ss or 0)
    try:
        return datetime(y, mo, d, hh, mm, ss)
    except Exception as e:
        print(f"How exceptional! {e}")
        pass


def set_fs_times_from_xmp(target_path: Path, creation_s: str, mod_s: str):
    """
    Set file system times from XMP strings.
    - Always sets mtime via os.utime if ModDate parsed.
    - On macOS, try to set creation time via 'SetFile -d'.
    
    Args:
        target_path: Target file path
        creation_s: Creation date string from XMP
        mod_s: Modification date string from XMP
    """
    mod_dt = parse_xmp_date(mod_s)
    cr_dt = parse_xmp_date(creation_s)
    
    # mtime/atime
    try:
        if mod_dt:
            ts = mod_dt.timestamp()
            os.utime(target_path, (ts, ts))
    except Exception:
        pass
    
    # creation time (macOS only)
    if sys.platform == "darwin" and cr_dt and have("SetFile"):
        try:
            # format: mm/dd/yy HH:MM:SS
            ds = cr_dt.strftime("%m/%d/%Y %H:%M:%S")
            run(["SetFile", "-d", ds, str(target_path)])
        except Exception:
            pass
    
    # try set modified via SetFile too (better fidelity on mac)
    if sys.platform == "darwin" and mod_dt and have("SetFile"):
        try:
            ds = mod_dt.strftime("%m/%d/%Y %H:%M:%S")
            run(["SetFile", "-m", ds, str(target_path)])
        except Exception:
            pass


def copy_fs_times(src: Path, dst: Path):
    """
    Copy file system times from source to destination file.
    
    Args:
        src: Source file path
        dst: Destination file path
    """
    try:
        st = src.stat()
        os.utime(dst, (st.st_atime, st.st_mtime))
        if sys.platform == "darwin" and have("SetFile"):
            # try to copy creation time using 'GetFileInfo' + 'SetFile -d'
            code, out, _ = run(["GetFileInfo", str(src)])
            # parse 'created:' and 'modified:' lines if present (best-effort)
            # otherwise we already set mtime above
            # Keep it simple; macOS creation time is optional
    except Exception:
        pass