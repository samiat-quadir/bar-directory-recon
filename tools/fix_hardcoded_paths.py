#!/usr/bin/env python3
"""
Fix Hardcoded Paths Tool

A simple script to find and fix hardcoded paths in a project.
"""

import os
import re
import argparse
import sys
from pathlib import Path


def os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')():
    """Get the OneDrive path for the current device."""
    # Try common locations first
    username = os.environ.get("USERNAME", "")
    possible_paths = [
        f"C:\\Users\\{username}\\OneDrive - Digital Age Marketing Group",
        f"C:\\Users\\samq\\OneDrive - Digital Age Marketing Group",
        f"C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_project_root_path():
    """Get the project root path."""
    # Get the current script directory and go up one level
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_file(file_path: str, fix: bool = False) -> int:
    """Scan a file for hardcoded paths and optionally fix them."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            print(f"Error reading {file_path} - skipping")
            return 0

    original_content = content
    issues_count = 0

    # Define the patterns to search for
    patterns = [
        (r"C:\\Users\\samq\\OneDrive - Digital Age Marketing Group", r"Get-OneDrivePath"),
        (r"C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group", r"Get-OneDrivePath"),
        (r"os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()", r"Get-OneDrivePath"),
        (r"os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()", r"Get-OneDrivePath"),
        (r"C:\\Users\\samq\\OneDrive", r"Get-OneDrivePath"),
        (r"C:\\Users\\samqu\\OneDrive", r"Get-OneDrivePath"),
        (r"os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()", r"Get-OneDrivePath"),
        (r"os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()", r"Get-OneDrivePath"),
    ]

    # Check for each pattern
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues_count += len(matches)
            print(f"Found {len(matches)} instances of '{pattern}' in {file_path}")

            if fix:
                # For PowerShell files
                if file_path.endswith(".ps1"):
                    content = re.sub(re.escape(pattern), "$(Get-OneDrivePath)", content)
                # For Python files
                elif file_path.endswith(".py"):
                    content = re.sub(re.escape(pattern), "os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()", content)
                # For Batch files, insert a variable
                elif file_path.endswith(".bat") or file_path.endswith(".cmd"):
                    # Insert a line at the top to get OneDrive path if not already there
                    if "for /f" not in content and "ONEDRIVE_PATH" not in content:
                        onedrive_setup = (
                            "for /f \"tokens=*\" %%a in ('powershell -NoProfile -ExecutionPolicy Bypass "
                            "-Command \"& { . '%~dp0tools\\DevicePathResolver.ps1'; Get-OneDrivePath }\"') do set ONEDRIVE_PATH=%%a\n\n"
                        )
                        content = onedrive_setup + content

                    content = re.sub(re.escape(pattern), "%ONEDRIVE_PATH%", content)
                # For Markdown and other text files, leave a comment
                else:
                    content = re.sub(re.escape(pattern), f"{pattern} <!-- TODO: Use device-agnostic path -->", content)

    # If content changed and fix is enabled, write the changes back
    if fix and content != original_content:
        print(f"Fixing {file_path}")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Successfully fixed {file_path}")
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")

    return issues_count


def scan_directory(directory, exclude_dirs=None, fix=False):
    """Scan a directory for hardcoded paths."""
    if exclude_dirs is None:
        exclude_dirs = {".git", ".venv", "venv", "__pycache__", "archive", "temp_backup", "temp_broken_code"}

    total_issues = 0

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Only scan text files
            if file.endswith((".py", ".ps1", ".bat", ".cmd", ".md", ".txt", ".json", ".html")):
                file_path = os.path.join(root, file)
                issues = scan_file(file_path, fix)
                total_issues += issues

    return total_issues


def main():
    parser = argparse.ArgumentParser(description="Scan for hardcoded paths")
    parser.add_argument("--fix", action="store_true", help="Fix the hardcoded paths")
    args = parser.parse_args()

    project_root = get_project_root_path()
    print(f"Scanning {project_root} for hardcoded paths...")

    total_issues = scan_directory(project_root, fix=args.fix)

    print(f"\nScan complete: Found {total_issues} hardcoded paths")
    if total_issues > 0 and not args.fix:
        print("Run with --fix to attempt automatic fixes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
