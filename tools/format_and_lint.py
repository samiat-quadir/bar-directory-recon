#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run project‑wide auto‑formatting (Black + isort), linting (flake8), and pre‑commit
hooks, then stage—and optionally commit—any changes.

Usage examples
--------------
# dry‑run (show diffs only)
python format_and_lint.py --dry-run

# format, run hooks, stage everything, commit with default message
python format_and_lint.py --commit

# same but custom commit message
python format_and_lint.py --commit "chore: auto‑format + lint fixes"

# only touch universal_recon/ and tools/
python format_and_lint.py universal_recon tools --commit
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], check: bool = True) -> int:
    """
    Execute *cmd* and stream output live.

    Parameters
    ----------
    cmd : list[str]
        Command and arguments to execute.
    check : bool, default True
        If *True* exit the script when the command returns non‑zero.

    Returns
    -------
    int
        The command's return‑code.
    """
    print(f"\n▶️  {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.stdout  # for typing
    for line in proc.stdout:
        print(line, end="")
    proc.wait()

    if check and proc.returncode:
        print(f"❌  command failed with code {proc.returncode}")
        sys.exit(proc.returncode)
    return proc.returncode


def git_changes_staged() -> bool:
    """Return *True* if there is anything staged for commit."""
    rc = subprocess.call(
        ["git", "diff", "--cached", "--quiet"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return rc != 0  # non‑zero means “there are differences”


def main() -> None:
    os.chdir(PROJECT_DIR)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Specific paths to format/lint (default: whole repo).",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying files.",
    )
    parser.add_argument(
        "-c",
        "--commit",
        nargs="?",
        const="chore: auto‑format & lint fixes",
        metavar='"msg"',
        help="Stage and commit with optional message.",
    )
    args = parser.parse_args()

    # 1️⃣  Black
    black_cmd = [sys.executable, "-m", "black", *args.paths]
    if args.dry_run:
        black_cmd.insert(black_cmd.index("black") + 1, "--check")
        black_cmd.insert(black_cmd.index("--check") + 1, "--diff")
    run(black_cmd)

    # 2️⃣  isort
    isort_cmd = [sys.executable, "-m", "isort", *args.paths]
    if args.dry_run:
        isort_cmd += ["--check-only", "--diff"]
    run(isort_cmd)

    # 3️⃣  flake8 (always run, even in dry‑run)
    run([sys.executable, "-m", "flake8", *args.paths], check=False)

    # 4️⃣  pre‑commit hooks
    if args.dry_run:
        print("ℹ️  Dry‑run: skipping pre‑commit hook execution.")
    else:
        run([sys.executable, "-m", "pre_commit", "run", "--all-files"], check=False)

    # stop here if no writes happened
    if args.dry_run:
        print("\n✅ Dry‑run complete — no files modified.")
        return

    # 5️⃣  Stage everything that changed
    run(["git", "add", *args.paths])

    # 6️⃣  Commit (optional)
    if args.commit:
        if git_changes_staged():
            run(["git", "commit", "-m", args.commit])
            print("✅ Changes committed.")
        else:
            print("ℹ️  No changes to commit.")


if __name__ == "__main__":
    main()
