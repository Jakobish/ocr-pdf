"""
Configuration management for the OCR PDF processor.

Goal: keep Python as a thin wrapper around `ocrmypdf` by only:
- loading settings
- scanning PDFs (include/exclude + recursion)
- building and running the `ocrmypdf` command
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "ocr_config.json"
DEFAULT_CONFIG: Dict[str, Any] = {
    "input_dir": ".",
    "include_glob": ["*.pdf"],
    "exclude_glob": ["OCR/**", "*/OCR/**"],
    "sort_by": "none",
    "max_files": 0,
    "print_every": 1,
    "jobs": "auto",
    "overwrite": False,
    "timeout": 0,
    # Passed verbatim to `ocrmypdf` (excluding input and output paths).
    "ocrmypdf_args": [
        "-l",
        "heb+eng",
        "--skip-text",
        "--rotate-pages",
        "--deskew",
        "--clean",
        "--output-type",
        "pdfa",
        "--optimize",
        "1",
    ],
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


def shlex_list(value: Any, default: List[str]) -> List[str]:
    """Parse a string or list into a list of CLI args."""
    if isinstance(value, list):
        items = [str(v) for v in value if str(v).strip()]
        return items or default
    if isinstance(value, tuple):
        items = [str(v) for v in value if str(v).strip()]
        return items or default
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return default
        import shlex

        return shlex.split(v)
    return default


def build_defaults(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete default configuration with user overrides."""
    merged = dict(DEFAULT_CONFIG)
    for key, value in (user_config or {}).items():
        merged[key] = unwrap_config_value(value)

    cpu_count = os.cpu_count()
    jobs_default = min(8, (cpu_count or 4))

    defaults = {
        "input_dir": stringish(merged.get("input_dir"), DEFAULT_CONFIG["input_dir"]),
        "include_glob": listish(
            merged.get("include_glob"), DEFAULT_CONFIG["include_glob"]
        ),
        "exclude_glob": listish(
            merged.get("exclude_glob"), DEFAULT_CONFIG["exclude_glob"]
        ),
        "sort_by": stringish(merged.get("sort_by"), DEFAULT_CONFIG["sort_by"]),
        "max_files": intish(merged.get("max_files"), DEFAULT_CONFIG["max_files"]),
        "print_every": intish(merged.get("print_every"), DEFAULT_CONFIG["print_every"]),
        "jobs": resolve_jobs(merged.get("jobs"), jobs_default),
        "overwrite": boolish(merged.get("overwrite"), DEFAULT_CONFIG["overwrite"]),
        "timeout": intish(merged.get("timeout"), DEFAULT_CONFIG["timeout"]),
        "ocrmypdf_args": shlex_list(
            merged.get("ocrmypdf_args"), DEFAULT_CONFIG["ocrmypdf_args"]
        ),
    }

    # Validate enum values
    if defaults["sort_by"] not in ("none", "path", "mtime", "size"):
        defaults["sort_by"] = DEFAULT_CONFIG["sort_by"]
    if defaults["max_files"] < 0:
        defaults["max_files"] = 0
    if defaults["print_every"] < 0:
        defaults["print_every"] = DEFAULT_CONFIG["print_every"]

    return defaults
