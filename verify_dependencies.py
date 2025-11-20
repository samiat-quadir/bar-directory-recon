#!/usr/bin/env python3
"""Compatibility wrapper for the new doctor module."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from bdr.doctor import format_report, run_doctor  # noqa: E402


def main() -> None:
    """Execute the doctor checks in no-exec mode."""

    report = run_doctor(no_exec=True)
    print(format_report(report), end="")


if __name__ == "__main__":
    main()
