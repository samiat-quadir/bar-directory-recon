#!/usr/bin/env python3
"""
Legacy Script Analyzer
======================

Finds PowerShell and Batch scripts that aren't referenced anywhere in the codebase.
"""

import os
import re
from pathlib import Path
from typing import Set, List, Dict


def find_all_scripts(root_dir: str) -> Set[str]:
    """Find all .bat and .ps1 files in the repository."""
    scripts = set()
    root_path = Path(root_dir)

    for pattern in ["**/*.bat", "**/*.ps1"]:
        for file_path in root_path.glob(pattern):
            # Skip files in excluded directories
            if any(excluded in str(file_path) for excluded in [".git", "__pycache__", ".venv", "node_modules"]):
                continue
            scripts.add(file_path.name)

    return scripts


def find_script_references(root_dir: str, scripts: Set[str]) -> Dict[str, List[str]]:
    """Find references to scripts in Python, Markdown, JSON, and YAML files."""
    references = {script: [] for script in scripts}
    root_path = Path(root_dir)

    # File extensions to search in
    search_extensions = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".rst"}

    for file_path in root_path.rglob("*"):
        if (
            file_path.is_file()
            and file_path.suffix in search_extensions
            and not any(excluded in str(file_path) for excluded in [".git", "__pycache__", ".venv", "node_modules"])
        ):

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for script in scripts:
                    # Remove extension for search to catch references without extension
                    script_base = os.path.splitext(script)[0]

                    # Look for script name (with or without extension)
                    if script in content or script_base in content:
                        # Verify it's actually a reference (not just part of another word)
                        pattern = r"\b" + re.escape(script_base) + r"(?:\.(?:bat|ps1))?\b"
                        if re.search(pattern, content, re.IGNORECASE):
                            references[script].append(str(file_path.relative_to(root_path)))

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return references


def main():
    """Main analysis function."""
    root_dir = os.getcwd()

    print("🔍 Analyzing PowerShell and Batch scripts...")
    print(f"📁 Root directory: {root_dir}")

    # Find all scripts
    scripts = find_all_scripts(root_dir)
    print(f"📄 Found {len(scripts)} scripts total")

    if scripts:
        print("🔍 Scripts found:")
        for script in sorted(scripts):
            print(f"   - {script}")
    else:
        print("⚠️  No scripts found!")

    # Find references
    references = find_script_references(root_dir, scripts)

    # Categorize scripts
    referenced_scripts = []
    unreferenced_scripts = []

    for script, refs in references.items():
        if refs:
            referenced_scripts.append((script, refs))
        else:
            unreferenced_scripts.append(script)

    # Report results
    print("\n" + "=" * 80)
    print("📊 SCRIPT ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\n✅ REFERENCED SCRIPTS ({len(referenced_scripts)}):")
    print("-" * 40)
    for script, refs in sorted(referenced_scripts):
        print(f"📄 {script}")
        for ref in refs[:3]:  # Show first 3 references
            print(f"   └─ {ref}")
        if len(refs) > 3:
            print(f"   └─ ... and {len(refs) - 3} more")
        print()

    print(f"\n❌ UNREFERENCED SCRIPTS ({len(unreferenced_scripts)}):")
    print("-" * 40)
    if unreferenced_scripts:
        for script in sorted(unreferenced_scripts):
            print(f"📄 {script}")

        print(f"\n🛠️  RECOMMENDED ACTIONS:")
        print("1. Review each unreferenced script to confirm it's not needed")
        print("2. Move legacy scripts to archive/legacy_scripts/ directory")
        print("3. Document any scripts that should be kept for manual use")
        print(f"4. Consider deleting truly obsolete scripts")

        # Show command to create archive directory and move files
        print(f"\n📁 To archive unreferenced scripts:")
        print("mkdir archive\\legacy_scripts")
        for script in sorted(unreferenced_scripts):
            print(f"move {script} archive\\legacy_scripts\\")

    else:
        print("✅ All scripts are referenced somewhere in the codebase!")

    print(f"\n📈 SUMMARY:")
    print(f"   Total scripts: {len(scripts)}")
    print(f"   Referenced: {len(referenced_scripts)}")
    print(f"   Unreferenced: {len(unreferenced_scripts)}")

    if unreferenced_scripts:
        print(f"   Cleanup potential: {len(unreferenced_scripts)} files")


if __name__ == "__main__":
    main()
