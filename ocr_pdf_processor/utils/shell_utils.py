"""
Shell utilities module for OCR PDF processor.
Provides functions for running shell commands and checking command availability.
"""
import subprocess
from typing import Tuple


def run(cmd, timeout=None) -> Tuple[int, str, str]:
    """
    Run a shell command and return its result.
    
    Args:
        cmd: Command list to execute
        timeout: Optional timeout in seconds
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return (
            p.returncode,
            p.stdout.decode("utf-8", "ignore"),
            p.stderr.decode("utf-8", "ignore"),
        )
    except FileNotFoundError:
        return 127, "", f"Command not found: {' '.join(cmd)}"
    except subprocess.TimeoutExpired:
        return 124, "", "Timeout"


def have(cmd_name: str) -> bool:
    """
    Check if a command is available in the system PATH.
    
    Args:
        cmd_name: Name of the command to check
        
    Returns:
        True if command exists, False otherwise
    """
    code, _, _ = run(["which", cmd_name])
    return code == 0