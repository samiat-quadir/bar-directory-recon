#!/usr/bin/env python3
"""
Fix Hardcoded Paths Tool

A simple script to find and fix hardcoded paths in a project.
This version repairs the corruption from merge conflicts.
"""

import argparse
import os
import re
import sys


def get_onedrive_path() -> str | None:
    """Get the OneDrive path for the current device."""
    # Try common locations first
    username = os.environ.get("USERNAME", "")
    possible_paths = [
        f"C:\\Users\\{username}\\OneDrive - Digital Age Marketing Group",
        "C:\\Users\\samq\\OneDrive - Digital Age Marketing Group",
        "C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_project_root_path() -> str:
    """Get the project root path."""
    # Get the current script directory and go up one level
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_file(file_path: str, fix: bool = False) -> int:
    """Scan a file for hardcoded paths and optionally fix them."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Error reading {file_path}: {e} - skipping")
        return 0

    original_content = content
    issues_count = 0

    # Define the patterns to search for - cleaned up from corruption
    patterns = [
        (
            r"C:\\Users\\samq\\OneDrive - Digital Age Marketing Group",
            "get_onedrive_path()",
        ),
        (
            r"C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group",
            "get_onedrive_path()",
        ),
        (r"C:\\Users\\samq\\OneDrive", "get_onedrive_path()"),
        (r"C:\\Users\\samqu\\OneDrive", "get_onedrive_path()"),
        # Remove any remaining corruption patterns
        (
            r"os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\)'\)",
            "get_onedrive_path()",
        ),
    ]

    # Check for each pattern
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues_count += len(matches)
            print(f"Found {len(matches)} instances of hardcoded path in {file_path}")

            if fix:
                # For PowerShell files
                if file_path.endswith(".ps1"):
                    content = re.sub(pattern, "$(Get-OneDrivePath)", content)
                # For Python files
                elif file_path.endswith(".py"):
                    content = re.sub(pattern, "get_onedrive_path()", content)
                # For Batch files, insert a variable
                elif file_path.endswith((".bat", ".cmd")):
                    # Insert a line at the top to get OneDrive path if not already there
                    if "ONEDRIVE_PATH" not in content:
                        onedrive_setup = (
                            "@echo off\n"
                            "REM Get OneDrive path dynamically\n"
                            'for /f "tokens=*" %%a in (\'powershell -NoProfile '
                            "-ExecutionPolicy Bypass -Command "
                            "\"[Environment]::GetFolderPath('UserProfile') + "
                            "'\\OneDrive - Digital Age Marketing Group'\"') "
                            "do set ONEDRIVE_PATH=%%a\n\n"
                        )
                        # Insert after first @echo off or at beginning
                        if "@echo off" in content:
                            content = content.replace("@echo off", onedrive_setup, 1)
                        else:
                            content = onedrive_setup + content

                    content = re.sub(pattern, "%ONEDRIVE_PATH%", content)
                # For other text files, leave a comment
                else:
                    content = re.sub(pattern, f"[DYNAMIC_PATH_NEEDED] <!-- {pattern} -->", content)

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


def scan_directory(directory: str, exclude_dirs: set[str] | None = None, fix: bool = False) -> int:
    """Scan a directory for hardcoded paths."""
    if exclude_dirs is None:
        exclude_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "archive",
            "temp_backup",
            "temp_broken_code",
            ".mypy_cache",
            "node_modules",
            "dist",
            "build",
        }

    total_issues = 0

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Only scan text files
            if file.endswith(
                (
                    ".py",
                    ".ps1",
                    ".bat",
                    ".cmd",
                    ".md",
                    ".txt",
                    ".json",
                    ".html",
                    ".yaml",
                    ".yml",
                )
            ):
                file_path = os.path.join(root, file)
                try:
                    issues = scan_file(file_path, fix)
                    total_issues += issues
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return total_issues


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Scan for hardcoded paths and fix them")
    parser.add_argument("--fix", action="store_true", help="Fix the hardcoded paths")
    parser.add_argument(
        "--directory", "-d", default=".", help="Directory to scan (default: current)"
    )
    args = parser.parse_args()

    project_root = os.path.abspath(args.directory)
    print(f"Scanning {project_root} for hardcoded paths...")

    total_issues = scan_directory(project_root, fix=args.fix)

    print(f"\nScan complete: Found {total_issues} hardcoded paths")
    if total_issues > 0 and not args.fix:
        print("Run with --fix to attempt automatic fixes")
    elif total_issues > 0 and args.fix:
        print("Attempted to fix all found issues")
    else:
        print("No hardcoded paths found!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
