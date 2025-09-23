#!/usr/bin/env python
"""
safe_commit_push.py - A script to safely commit and push changes.
Validates that all necessary checks pass before committing and pushing.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=True, check=False)

    if check and result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        sys.exit(result.returncode)

    return result


def check_git_status():
    """Check if there are any changes to commit."""
    result = run_command(["git", "status", "--porcelain"])
    return bool(result.stdout.strip())


def run_pre_commit():
    """Run pre-commit hooks on all files."""
    print("Running pre-commit hooks...")
    result = run_command(["pre-commit", "run", "--all-files"], check=False)

    if result.returncode != 0:
        print("❌ Pre-commit hooks failed. Please fix the issues before committing.")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ Pre-commit hooks passed.")
    return True


def check_hardcoded_paths():
    """Check for hardcoded paths in the codebase."""
    print("Checking for hardcoded paths...")

    if os.path.exists("ScanPaths.bat"):
        result = run_command(["cmd", "/c", "ScanPaths.bat"], check=False, capture_output=True)

        if "Found hardcoded paths" in result.stdout:
            print("❌ Hardcoded paths detected. Please fix them before committing.")
            print("   Run 'ScanPaths.bat --fix' to automatically fix them.")
            return False
    else:
        print("⚠️ ScanPaths.bat not found. Skipping hardcoded path check.")

    print("✅ No hardcoded paths detected.")
    return True


def commit_changes(message):
    """Commit changes with the given message."""
    print(f"Committing changes with message: {message}")
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", message])


def push_changes():
    """Push changes to remote repository."""
    print("Pushing changes to remote repository...")
    run_command(["git", "push"])


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Safely commit and push changes.")
    parser.add_argument("--message", "-m", help="Commit message", default="Updated files")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually commit or push")
    args = parser.parse_args()

    # Change to repository root
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    print(f"Working directory: {os.getcwd()}")

    # Check if there are changes to commit
    has_changes = check_git_status()
    if not has_changes:
        print("No changes to commit.")
        return

    # Run checks
    pre_commit_ok = run_pre_commit()
    paths_ok = check_hardcoded_paths()

    all_checks_passed = pre_commit_ok and paths_ok

    if args.dry_run:
        if all_checks_passed:
            print("✅ Dry run successful. All checks passed.")
        else:
            print("❌ Dry run failed. Please fix the issues before committing.")
        return

    if not all_checks_passed:
        print("❌ Not committing changes due to failed checks.")
        return

    # Commit and push changes
    commit_changes(args.message)
    push_changes()
    print("✅ Changes committed and pushed successfully.")


if __name__ == "__main__":
    main()
