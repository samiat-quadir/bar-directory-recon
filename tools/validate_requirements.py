#!/usr/bin/env python3
"""
Requirements Validation Script

This script validates that requirements files contain the correct dependencies
and constraints to prevent known issues from recurring.

Known Issues to Check:
1. watchdog>=3.0.0 should be watchdog>=6.0.0,<7.0.0
2. smtplib-ssl should not be present (non-existent package)
3. Other known problematic dependencies

Usage:
    python validate_requirements.py
    python validate_requirements.py --fix
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Known problematic dependencies and their fixes
DEPENDENCY_FIXES = {
    "requirements-core.txt": {
        "watchdog>=3.0.0": "watchdog>=6.0.0,<7.0.0",
        "watchdog==3.0.0": "watchdog>=6.0.0,<7.0.0",
        "watchdog>3.0.0": "watchdog>=6.0.0,<7.0.0",
    },
    "requirements-optional.txt": {
        "smtplib-ssl": None,  # Remove entirely
    },
}

# Dependencies that should never be present
FORBIDDEN_DEPENDENCIES = [
    "smtplib-ssl",  # Non-existent package
]


def validate_file(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Validate a requirements file and return list of issues.

    Returns:
        List of tuples: (line_number, issue_description, suggested_fix)
    """
    issues = []

    if not file_path.exists():
        return [("N/A", f"File not found: {file_path}", "Create the file")]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [("N/A", f"Error reading {file_path}: {e}", "Fix file permissions")]

    file_name = file_path.name
    file_fixes = DEPENDENCY_FIXES.get(file_name, {})

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Check for forbidden dependencies
        for forbidden in FORBIDDEN_DEPENDENCIES:
            if forbidden in line:
                issues.append((str(line_num), f"Forbidden dependency found: {forbidden}", "Remove this line entirely"))

        # Check for watchdog version issues specifically
        if re.search(r"watchdog>=3\.\d+\.\d+", line):
            issues.append((str(line_num), "Outdated dependency: watchdog>=3.x.x", "Change to: watchdog>=6.0.0,<7.0.0"))

        # Check for specific fixes from our known patterns
        for old_pattern, new_pattern in file_fixes.items():
            if old_pattern in line:
                if new_pattern is None:
                    fix_msg = "Remove this line entirely"
                else:
                    fix_msg = f"Change to: {new_pattern}"

                issues.append((str(line_num), f"Outdated dependency: {old_pattern}", fix_msg))

    return issues


def fix_file(file_path: Path) -> bool:
    """
    Automatically fix known issues in a requirements file.

    Returns:
        True if fixes were applied, False otherwise
    """
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

    original_content = content
    file_name = file_path.name
    file_fixes = DEPENDENCY_FIXES.get(file_name, {})

    # Apply watchdog version fixes
    content = re.sub(r"watchdog>=3\.\d+\.\d+", "watchdog>=6.0.0,<7.0.0", content)

    # Apply specific dependency fixes
    for old_dep, new_dep in file_fixes.items():
        if old_dep in content:
            if new_dep is None:
                # Remove the entire line containing this dependency
                lines = content.split("\n")
                filtered_lines = []
                for line in lines:
                    if old_dep not in line:
                        filtered_lines.append(line)
                    else:
                        print(f"🔧 Removing line: {line.strip()}")
                content = "\n".join(filtered_lines)
            else:
                print(f"🔧 Replacing {old_dep} with {new_dep}")
                content = content.replace(old_dep, new_dep)

    # Remove forbidden dependencies
    for forbidden in FORBIDDEN_DEPENDENCIES:
        if forbidden in content:
            lines = content.split("\n")
            filtered_lines = []
            for line in lines:
                if forbidden not in line:
                    filtered_lines.append(line)
                else:
                    print(f"🔧 Removing forbidden dependency: {line.strip()}")
            content = "\n".join(filtered_lines)

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Fixed {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing to {file_path}: {e}")
            return False
    else:
        return False


def main():
    """Main function to validate and optionally fix requirements files."""
    parser = argparse.ArgumentParser(description="Validate requirements files for known issues")
    parser.add_argument("--fix", action="store_true", help="Automatically fix detected issues")
    parser.add_argument("--files", nargs="*", help="Specific files to check (default: all known requirements files)")

    args = parser.parse_args()

    # Determine which files to check
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        # Default files to check
        project_root = Path.cwd()
        files_to_check = [
            project_root / "requirements.txt",
            project_root / "requirements-core.txt",
            project_root / "requirements-optional.txt",
        ]
        # Only check files that exist
        files_to_check = [f for f in files_to_check if f.exists()]

    if not files_to_check:
        print("❌ No requirements files found to validate")
        return 1

    print("🔍 Validating requirements files...")
    print(f"📁 Project root: {Path.cwd()}")

    total_issues = 0
    files_with_fixes = 0

    for file_path in files_to_check:
        print(f"📋 Checking {file_path.name}...")

        if args.fix:
            # Try to fix issues
            if fix_file(file_path):
                files_with_fixes += 1
                print(f"🔧 Applied fixes to {file_path.name}")
            else:
                print(f"✅ {file_path.name}: No fixes needed")
        else:
            # Just validate and report issues
            issues = validate_file(file_path)
            if issues:
                print(f"⚠️ {file_path.name}: {len(issues)} issues found")
                for line_num, issue, suggestion in issues:
                    print(f"   Line {line_num}: {issue}")
                    print(f"   Suggestion: {suggestion}")
                total_issues += len(issues)
            else:
                print(f"✅ {file_path.name}: No issues found")

    # Summary
    if args.fix:
        print(f"📊 Summary:")
        print(f"   Files processed: {len(files_to_check)}")
        print(f"   Files with fixes applied: {files_with_fixes}")
        if files_with_fixes > 0:
            print("🎉 Fixes completed!")
        else:
            print("🎉 All files were already valid!")
    else:
        print(f"📊 Summary:")
        print(f"   Files checked: {len(files_to_check)}")
        print(f"   Total issues found: {total_issues}")
        if total_issues == 0:
            print("🎉 All requirements files are valid!")
        else:
            print("⚠️ Issues found. Run with --fix to apply automatic fixes.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
