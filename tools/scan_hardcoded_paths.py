#!/usr/bin/env python3
"""
Scan for Hardcoded Paths in Python Files

This script scans Python files for hardcoded paths that might cause
cross-device compatibility issues and suggests replacements.
"""

import os
import re
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional

# Import our device path resolver if possible
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
    from device_path_resolver import get_project_root_path, os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')
    RESOLVER_AVAILABLE = True
except ImportError:
    RESOLVER_AVAILABLE = False

# Patterns to search for - add any specific patterns relevant to your environment
PATH_PATTERNS = [
    r'C:\\Users\\samq\\OneDrive',
    r'C:\\Users\\samqu\\OneDrive',
    r'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()',
    r'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()',
    r'C:\\Users\\samq\\OneDrive - Digital Age Marketing Group',
    r'C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group',
    r'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()',
    r'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()',
    r'samq\\OneDrive',
    r'samqu\\OneDrive'
]

# Directories to exclude
EXCLUDE_DIRS = {
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    'archive',
    'temp_backup',
    'temp_broken_code',
    'htmlcov'
}

# File extensions to scan
FILE_EXTENSIONS = {
    '.py',
    '.ipynb',
    '.md',
    '.rst',
    '.txt',
    '.yaml',
    '.yml',
    '.json'
}

class PathScanner:
    """Scans files for hardcoded paths and suggests alternatives."""

    def __init__(self, project_root: str, fix: bool = False):
        self.project_root = project_root
        self.fix = fix
        self.patterns = [re.compile(pattern) for pattern in PATH_PATTERNS]
        self.issues_found = 0
        self.files_with_issues = 0
        self.files_fixed = 0

    def get_files_to_scan(self) -> List[str]:
        """Return a list of files to scan."""
        all_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()

                if ext in FILE_EXTENSIONS:
                    all_files.append(file_path)

        return all_files

    def scan_file(self, file_path: str) -> int:
        """
        Scan a file for hardcoded paths.
        Returns the number of issues found.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"⚠️  Skipping binary file: {file_path}")
            return 0

        issues = 0

        for pattern in self.patterns:
            matches = pattern.finditer(content)
            for match in matches:
                issues += 1
                matched_text = match.group(0)
                line_number = content[:match.start()].count('\n') + 1

                print(f"\n🔴 Issue in {file_path}:{line_number}")

                # Extract the line containing the match
                lines = content.split('\n')
                line = lines[line_number - 1]

                print(f"  Line: {line}")
                print(f"  Hardcoded path: {matched_text}")

                # Suggest a fix
                if RESOLVER_AVAILABLE:
                    if file_path.endswith('.py'):
                        rel_path = self._get_relative_path(matched_text)
                        suggestion = f"os.path.join(get_project_root_path(), '{rel_path}')"
                    else:
                        suggestion = "Use device_path_resolver functions instead of hardcoded paths"
                else:
                    suggestion = "Use device_path_resolver.py for cross-device compatibility"

                print(f"  Suggested fix: {suggestion}")

                # Apply the fix if requested
                if self.fix and file_path.endswith('.py') and RESOLVER_AVAILABLE:
                    rel_path = self._get_relative_path(matched_text)
                    new_content = content.replace(
                        matched_text,
                        f"os.path.join(get_project_root_path(), '{rel_path}')"
                    )

                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"  ✅ Fixed issue in {file_path}")
                        content = new_content  # Update content for subsequent matches
                        self.files_fixed += 1

        if issues > 0:
            self.files_with_issues += 1

        self.issues_found += issues
        return issues

    def _get_relative_path(self, full_path: str) -> str:
        """Convert absolute path to relative path from project root."""
        if not RESOLVER_AVAILABLE:
            return full_path

        # Normalize path separators
        norm_path = full_path.replace('\\', '/')

        # Get project root and OneDrive path
        onedrive_path = os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'os.path.join(get_project_root_path(), 'get_onedrive_path')')')')')')')')')')')')')')')')')')')')')')')')()
        if onedrive_path:
            norm_onedrive = onedrive_path.replace('\\', '/')

            # Check if the path starts with OneDrive path
            if norm_path.startswith(norm_onedrive):
                relative = norm_path[len(norm_onedrive):].lstrip('/')
                return relative

        # If we can't determine the relative path, return the original
        return full_path

    def scan_all_files(self) -> None:
        """Scan all files in the project."""
        files = self.get_files_to_scan()
        print(f"🔍 Scanning {len(files)} files for hardcoded paths...")

        for file_path in files:
            self.scan_file(file_path)

        print("\n" + "="*70)
        print(f"📊 Scan complete: {self.issues_found} issues found in {self.files_with_issues} files")

        if self.fix:
            print(f"🛠️  Fixed issues in {self.files_fixed} files")
        elif self.issues_found > 0:
            print("💡 Run with --fix to automatically fix issues")

        if self.issues_found == 0:
            print("✅ No hardcoded paths found!")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Scan Python files for hardcoded paths that might cause cross-device compatibility issues"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix detected issues"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Project root directory to scan (default: parent of script directory)"
    )

    args = parser.parse_args()

    if not RESOLVER_AVAILABLE:
        print("⚠️  Warning: device_path_resolver.py not found. Some features will be limited.")

    scanner = PathScanner(args.path, args.fix)
    scanner.scan_all_files()

    # Return non-zero exit code if issues were found
    return 1 if scanner.issues_found > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
