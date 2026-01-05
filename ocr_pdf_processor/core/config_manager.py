"""
Configuration management module for OCR PDF processor.
Handles loading, parsing, and validating configuration from files and command line arguments.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "ocr_config.json"
DEFAULT_CONFIG = {
    "input_dir": ".",
    "output_dir": "./out_pdfs",
    "include_glob": ["*.pdf"],
    "exclude_glob": [],
    "exclude_output_dir": True,
    "sort_by": "none",
    "max_files": 0,
    "print_every": 1,
    "lang": "heb+eng",
    "optimize": 1,
    "skip_big_mb": 2048,
    "jobs": "auto",
    "ocr_jobs": "auto",
    "redo_policy": "auto",
    "dup_threshold": 0.15,
    "force_ocr_all": False,
    "overwrite": False,
    "in_place": False,
    "resume_from_csv": False,
    "csv_append": False,
    "preserve_fstimes": "xmp",
    "timeout": 0,
    "text_sample_pages": 3,
    "tesseract_time": 0,
    "tesseract_pagesegmode": 0,
    "csv": "ocr_report.csv",
}


def parse_config_path(argv):
    """Parse command line arguments to extract config file path."""
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--config", type=Path)
    ns, _ = ap.parse_known_args(argv)
    if ns.config:
        return ns.config, True
    return DEFAULT_CONFIG_PATH, False


def load_config(path: Path, required: bool) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not path:
        return {}
    path = path.expanduser()
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        if required:
            print(f"Config file not found: {path}", file=sys.stderr)
            sys.exit(2)
        return {}
    except json.JSONDecodeError as e:
        if required:
            print(f"Invalid JSON in config: {path} ({e})", file=sys.stderr)
            sys.exit(2)
        return {}
    except Exception as e:
        if required:
            print(f"Failed to read config: {path} ({e})", file=sys.stderr)
            sys.exit(2)
        return {}
    if not isinstance(data, dict):
        if required:
            print(f"Config must be a JSON object: {path}", file=sys.stderr)
            sys.exit(2)
        return {}
    return data


def unwrap_config_value(value):
    """Unwrap configuration values that might be nested in 'value' key."""
    if isinstance(value, dict) and "value" in value:
        return value.get("value")
    return value


def stringish(value: Any, default: str) -> str:
    """Convert value to string if possible, otherwise return default."""
    if isinstance(value, str) and value.strip():
        return value
    return default


def boolish(value: Any, default: bool) -> bool:
    """Convert value to boolean if possible, otherwise return default."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("1", "true", "yes", "y", "on"):
            return True
        if v in ("0", "false", "no", "n", "off"):
            return False
    return default


def intish(value: Any, default: int) -> int:
    """Convert value to integer if possible, otherwise return default."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def floatish(value: Any, default: float) -> float:
    """Convert value to float if possible, otherwise return default."""
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def listish(value: Any, default: list) -> list:
    """Convert value to list if possible, otherwise return default."""
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
        return items or default
    if isinstance(value, tuple):
        items = [str(v).strip() for v in value if str(v).strip()]
        return items or default
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return default
        parts = [p.strip() for p in v.split(",") if p.strip()]
        return parts or default
    return default


def resolve_jobs(value: Any, fallback: int) -> int:
    """Resolve job count, handling 'auto' values."""
    if value is None:
        return fallback
    if isinstance(value, str) and value.strip().lower() == "auto":
        return fallback
    return intish(value, fallback)


def build_defaults(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete default configuration with user overrides."""
    merged = dict(DEFAULT_CONFIG)
    for key, value in (user_config or {}).items():
        merged[key] = unwrap_config_value(value)

    cpu_count = os.cpu_count()
    jobs_default = min(8, (cpu_count or 4))
    ocr_jobs_default = min(4, (cpu_count or 2))

    defaults = {
        "input_dir": stringish(merged.get("input_dir"), DEFAULT_CONFIG["input_dir"]),
        "output_dir": stringish(merged.get("output_dir"), DEFAULT_CONFIG["output_dir"]),
        "include_glob": listish(merged.get("include_glob"), DEFAULT_CONFIG["include_glob"]),
        "exclude_glob": listish(merged.get("exclude_glob"), DEFAULT_CONFIG["exclude_glob"]),
        "exclude_output_dir": boolish(merged.get("exclude_output_dir"), DEFAULT_CONFIG["exclude_output_dir"]),
        "sort_by": stringish(merged.get("sort_by"), DEFAULT_CONFIG["sort_by"]),
        "max_files": intish(merged.get("max_files"), DEFAULT_CONFIG["max_files"]),
        "print_every": intish(merged.get("print_every"), DEFAULT_CONFIG["print_every"]),
        "lang": stringish(merged.get("lang"), DEFAULT_CONFIG["lang"]),
        "optimize": intish(merged.get("optimize"), DEFAULT_CONFIG["optimize"]),
        "skip_big_mb": intish(merged.get("skip_big_mb"), DEFAULT_CONFIG["skip_big_mb"]),
        "jobs": resolve_jobs(merged.get("jobs"), jobs_default),
        "ocr_jobs": resolve_jobs(merged.get("ocr_jobs"), ocr_jobs_default),
        "redo_policy": stringish(merged.get("redo_policy"), DEFAULT_CONFIG["redo_policy"]),
        "dup_threshold": floatish(merged.get("dup_threshold"), DEFAULT_CONFIG["dup_threshold"]),
        "force_ocr_all": boolish(merged.get("force_ocr_all"), DEFAULT_CONFIG["force_ocr_all"]),
        "overwrite": boolish(merged.get("overwrite"), DEFAULT_CONFIG["overwrite"]),
        "in_place": boolish(merged.get("in_place"), DEFAULT_CONFIG["in_place"]),
        "resume_from_csv": boolish(merged.get("resume_from_csv"), DEFAULT_CONFIG["resume_from_csv"]),
        "csv_append": boolish(merged.get("csv_append"), DEFAULT_CONFIG["csv_append"]),
        "preserve_fstimes": stringish(merged.get("preserve_fstimes"), DEFAULT_CONFIG["preserve_fstimes"]),
        "timeout": intish(merged.get("timeout"), DEFAULT_CONFIG["timeout"]),
        "text_sample_pages": intish(merged.get("text_sample_pages"), DEFAULT_CONFIG["text_sample_pages"]),
        "tesseract_time": intish(merged.get("tesseract_time"), DEFAULT_CONFIG["tesseract_time"]),
        "tesseract_pagesegmode": intish(merged.get("tesseract_pagesegmode"), DEFAULT_CONFIG["tesseract_pagesegmode"]),
        "csv": stringish(merged.get("csv"), DEFAULT_CONFIG["csv"]),
    }

    # Validate enum values
    if defaults["redo_policy"] not in ("auto", "aggressive", "never"):
        defaults["redo_policy"] = DEFAULT_CONFIG["redo_policy"]
    if defaults["preserve_fstimes"] not in ("xmp", "fs", "none"):
        defaults["preserve_fstimes"] = DEFAULT_CONFIG["preserve_fstimes"]
    if defaults["sort_by"] not in ("none", "path", "mtime", "size"):
        defaults["sort_by"] = DEFAULT_CONFIG["sort_by"]
    if defaults["max_files"] < 0:
        defaults["max_files"] = 0
    if defaults["print_every"] < 0:
        defaults["print_every"] = DEFAULT_CONFIG["print_every"]
    if defaults["text_sample_pages"] < 1:
        defaults["text_sample_pages"] = DEFAULT_CONFIG["text_sample_pages"]

    return defaults