#!/usr/bin/env python3
"""
BOM Detection Script for YAML/Config Files

Scans for UTF-8 BOM (Byte Order Mark) in YAML and config files that could
cause parsing errors in Docker containers and other tools.

Usage:
    python tools/check_bom.py [--fix]

Options:
    --fix    Remove BOMs from detected files
"""

import argparse
import sys
from pathlib import Path


def has_bom(file_path: Path) -> bool:
    """Check if file starts with UTF-8 BOM."""
    try:
        with open(file_path, "rb") as f:
            return f.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


def remove_bom(file_path: Path) -> bool:
    """Remove UTF-8 BOM from file. Returns True if BOM was removed."""
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        if content.startswith(b"\xef\xbb\xbf"):
            with open(file_path, "wb") as f:
                f.write(content[3:])  # Skip BOM bytes
            return True
        return False
    except OSError as e:
        print(f"Error processing {file_path}: {e}")
        return False


def scan_files(root_dir: Path) -> list[Path]:
    """Find YAML and config files that might have BOM issues."""
    patterns = [
        "**/*.yml",
        "**/*.yaml",
        "**/*.json",
        "**/prometheus.yml",
        "**/docker-compose.yml",
        "**/alertmanager.yml",
        "**/.env*",
    ]

    files: set[Path] = set()
    for pattern in patterns:
        files.update(root_dir.glob(pattern))

    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description="Detect and optionally fix UTF-8 BOM in config files"
    )
    parser.add_argument("--fix", action="store_true", help="Remove BOMs from detected files")
    parser.add_argument("--directory", default=".", help="Directory to scan (default: current)")
    args = parser.parse_args()

    root_dir = Path(args.directory).resolve()
    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist")
        sys.exit(1)

    print(f"Scanning {root_dir} for UTF-8 BOM in config files...")

    files_to_check = scan_files(root_dir)
    bom_files = []

    for file_path in files_to_check:
        if has_bom(file_path):
            bom_files.append(file_path)

    if not bom_files:
        print("✅ No UTF-8 BOM detected in config files")
        return 0

    print(f"\n⚠️  Found {len(bom_files)} files with UTF-8 BOM:")
    for file_path in bom_files:
        rel_path = file_path.relative_to(root_dir)
        print(f"  - {rel_path}")

    if args.fix:
        print("\n🔧 Removing BOMs...")
        fixed_count = 0
        for file_path in bom_files:
            if remove_bom(file_path):
                rel_path = file_path.relative_to(root_dir)
                print(f"  ✅ Fixed: {rel_path}")
                fixed_count += 1

        print(f"\n✅ Removed BOM from {fixed_count} files")
        return 0 if fixed_count == len(bom_files) else 1
    else:
        print("\nRun with --fix to remove BOMs automatically")
        print("Or manually remove BOMs with your editor")
        return 1


if __name__ == "__main__":
    sys.exit(main())
