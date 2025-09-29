#!/usr/bin/env python3
"""
Hardcoded Path Scanner
=====================

Scans the codebase for hardcoded paths and suggests replacements.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import our device path resolver if possible
try:
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"
        ),
    )

    RESOLVER_AVAILABLE = True
except ImportError:
    RESOLVER_AVAILABLE = False

# Patterns to search for - add any specific patterns relevant to your environment
PATH_PATTERNS = [
    r"C:\\Users\\samq\\OneDrive",
    r"C:\\Users\\samqu\\OneDrive",
    r"C:\\bar-directory-recon",
    r"C:\\Code\\bar-directory-recon",
    r"C:\\Users\\samq\\OneDrive - Digital Age Marketing Group",
    r"C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group",
    r"/c/",
    r"/mnt/c/",
    r"C:\\Users\\samq\\\.venv",
    r"C:\\Users\\samqu\\\.venv",
    r"samq\\OneDrive",
    r"samqu\\OneDrive",
    r"erssamq.*OneDrive",
    r"erssamqu.*OneDrive",
]

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    r"\.git",
    r"\.vscode",
    r"__pycache__",
    r"\.pyc$",
    r"node_modules",
    r"\.log$",
    r"\.tmp$",
    r"\.cache",
    r"logs[\\/]",
    r"output[\\/]",
    r"temp_backup[\\/]",
    r"archive[\\/]",
    r"htmlcov[\\/]",
]

# File extensions to scan
SCAN_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".bat",
    ".ps1",
    ".sh",
}


class HardcodedPathScanner:
    """Scanner for hardcoded paths in codebase."""

    def __init__(self, root_dir: str = None, fix: bool = False):
        self.root_dir = Path(root_dir or os.getcwd())
        self.fix = fix
        self.findings: List[Dict[str, str]] = []
        self.files_fixed = 0

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        path_str = str(file_path.relative_to(self.root_dir))
        for pattern in EXCLUDE_PATTERNS:
            if re.search(pattern, path_str):
                return True
        return False

    def scan_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Scan a single file for hardcoded paths."""
        findings = []

        # Only scan files with relevant extensions
        if file_path.suffix.lower() not in SCAN_EXTENSIONS:
            return findings

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.splitlines()

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return findings

        # Track if we made any changes for fixing
        original_content = content

        for line_num, line in enumerate(lines, 1):
            for pattern in PATH_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    finding = {
                        "file": str(file_path.relative_to(self.root_dir)),
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group(),
                        "full_line": line.strip(),
                        "suggestion": self._get_suggestion(match.group()),
                        "fixed": False,
                    }

                    # Apply fix if requested
                    if self.fix:
                        replacement = self._get_replacement(match.group())
                        if replacement and replacement != match.group():
                            content = content.replace(match.group(), replacement)
                            finding["fixed"] = True
                            finding["replacement"] = replacement

                    findings.append(finding)

        # Write fixed content back to file
        if self.fix and content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.files_fixed += 1
                print(
                    f"✅ Fixed hardcoded paths in {file_path.relative_to(self.root_dir)}"
                )
            except Exception as e:
                print(f"Error writing fixed content to {file_path}: {e}")

        return findings

    def _get_suggestion(self, hardcoded_path: str) -> str:
        """Get suggestion for replacing hardcoded path."""
        if "OneDrive" in hardcoded_path:
            if RESOLVER_AVAILABLE:
                return "get_onedrive_path() or ${ONEDRIVE_PATH}"
            else:
                return "${ONEDRIVE_PATH} environment variable"
        elif "bar-directory-recon" in hardcoded_path:
            if RESOLVER_AVAILABLE:
                return "get_project_root_path() or ${PROJECT_ROOT}"
            else:
                return "${PROJECT_ROOT} environment variable"
        elif ".venv" in hardcoded_path:
            return "os.path.join(get_project_root_path(), '.venv')"
        else:
            return "Use relative path or environment variable"

    def _get_replacement(self, hardcoded_path: str) -> Optional[str]:
        """Get replacement text for hardcoded path."""
        if not RESOLVER_AVAILABLE:
            return None

        if "OneDrive" in hardcoded_path and "bar-directory-recon" in hardcoded_path:
            return "get_project_root_path()"
        elif "OneDrive" in hardcoded_path:
            return "get_onedrive_path()"
        elif "bar-directory-recon" in hardcoded_path:
            return "get_project_root_path()"

        return None

    def scan_all_files(self) -> None:
        """Scan all files in the directory."""
        print(f"🔍 Scanning for hardcoded paths in {self.root_dir}")
        if self.fix:
            print("🛠️  Fix mode enabled - will attempt to fix issues automatically")

        file_count = 0
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and not self.should_exclude_file(file_path):
                findings = self.scan_file(file_path)
                self.findings.extend(findings)
                file_count += 1

        print(f"📊 Scanned {file_count} files")

    def generate_report(self) -> None:
        """Generate and print the findings report."""
        if not self.findings:
            print("✅ No hardcoded paths found!")
            return

        print(f"\n🔍 Found {len(self.findings)} hardcoded path issues:")
        print("=" * 80)

        # Group by file
        files = {}
        fixed_count = 0
        for finding in self.findings:
            file_path = finding["file"]
            if file_path not in files:
                files[file_path] = []
            files[file_path].append(finding)
            if finding.get("fixed", False):
                fixed_count += 1

        for file_path, file_findings in sorted(files.items()):
            print(f"\n📄 {file_path}")
            print("-" * 50)

            for finding in file_findings:
                status = "✅ FIXED" if finding.get("fixed", False) else "❌ ISSUE"
                print(f"  {status} Line {finding['line']}: {finding['match']}")

                if finding.get("fixed", False):
                    print(f"    🔄 Replaced with: {finding.get('replacement', 'N/A')}")
                else:
                    print(f"    💡 Suggestion: {finding['suggestion']}")

                # Show context (truncated)
                context = finding["full_line"]
                if len(context) > 100:
                    context = context[:97] + "..."
                print(f"    📝 Context: {context}")
                print()

        # Summary
        print("=" * 80)
        if self.fix:
            print(f"✅ Fixed {fixed_count} issues in {self.files_fixed} files")
            remaining = len(self.findings) - fixed_count
            if remaining > 0:
                print(f"⚠️  {remaining} issues require manual review")
        else:
            print(f"🛠️  Run with --fix to automatically fix {len(self.findings)} issues")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scan for hardcoded paths that cause cross-device compatibility issues"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix detected issues where possible",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory to scan (default: current directory)",
    )

    args = parser.parse_args()

    if not RESOLVER_AVAILABLE:
        print(
            "⚠️  Warning: device_path_resolver.py not available. Fix mode will be limited."
        )

    scanner = HardcodedPathScanner(args.directory, args.fix)
    scanner.scan_all_files()
    scanner.generate_report()

    if scanner.findings:
        print("\n🛠️  To fix these issues:")
        print("1. Replace hardcoded paths with environment variables")
        print("2. Use relative paths where possible")
        print("3. Use device_path_resolver functions for cross-device compatibility")

        # Exit with non-zero code if unfixed issues remain
        if not args.fix or any(not f.get("fixed", False) for f in scanner.findings):
            sys.exit(1)
    else:
        print("✅ All clear!")
        sys.exit(0)


if __name__ == "__main__":
    main()
