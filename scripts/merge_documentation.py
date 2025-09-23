#!/usr/bin/env python3
"""
Documentation Merger Script
==========================

Merges multiple README phase files into a cohesive documentation structure,
preserving headings and creating a unified table of contents.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


class DocumentationMerger:
    """Merges multiple markdown files into unified documentation."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)

    def find_readme_files(self) -> list[Path]:
        """Find all README files in the project."""
        patterns = ["README*.md", "PHASE*README*.md", "*_README.md", "README_*.md"]

        files: list[Path] = []
        for pattern in patterns:
            files.extend(self.project_root.glob(pattern))

        # Sort by modification time for logical ordering
        return sorted(files, key=lambda f: f.stat().st_mtime)

    def extract_metadata(self, file_path: Path) -> dict[str, str]:
        """Extract metadata from markdown file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Extract title (first h1)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Extract phase/version info
        phase_match = re.search(r"(?i)phase\s*(\d+)", title)
        phase = phase_match.group(1) if phase_match else "0"

        # Extract date
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content)
        date = date_match.group(1) if date_match else "unknown"

        return {
            "title": title,
            "phase": phase,
            "date": date,
            "filename": file_path.name,
        }

    def adjust_heading_levels(self, content: str, base_level: int = 2) -> str:
        """Adjust heading levels to fit into document hierarchy."""
        lines = content.split("\n")
        adjusted_lines = []

        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r"^(#+)\s+(.+)$", line)
            if heading_match:
                current_level = len(heading_match.group(1))
                new_level = current_level + base_level - 1
                # Ensure we don't exceed h6
                new_level = min(new_level, 6)
                adjusted_lines.append("#" * new_level + " " + heading_match.group(2))
            else:
                adjusted_lines.append(line)

        return "\n".join(adjusted_lines)

    def create_table_of_contents(self, files_metadata: list[dict]) -> str:
        """Create table of contents for merged documentation."""
        toc = ["# Table of Contents\n"]

        # Group by phase
        by_phase: dict[str, list[dict]] = {}
        for meta in files_metadata:
            phase = meta["phase"]
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(meta)

        # Generate TOC
        for phase in sorted(by_phase.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            if phase != "0":
                toc.append(f"## Phase {phase}")
            else:
                toc.append("## General Documentation")

            for meta in by_phase[phase]:
                # Create anchor link
                anchor = re.sub(r"[^\w\s-]", "", meta["title"].lower())
                anchor = re.sub(r"[-\s]+", "-", anchor)
                toc.append(f"- [{meta['title']}](#{anchor})")
                toc.append(f"  - File: `{meta['filename']}`")
                toc.append(f"  - Date: {meta['date']}")

            toc.append("")

        return "\n".join(toc)

    def merge_files(self, output_path: Path | None = None) -> Path:
        """Merge all README files into unified documentation."""
        if output_path is None:
            output_path = self.docs_dir / "README.md"

        # Find and analyze files
        readme_files = self.find_readme_files()
        files_metadata = []

        print(f"Found {len(readme_files)} README files to merge:")
        for file_path in readme_files:
            meta = self.extract_metadata(file_path)
            files_metadata.append(meta)
            print(f"  - {file_path.name} (Phase {meta['phase']}, {meta['date']})")

        # Start building merged content
        merged_content = []

        # Header
        merged_content.append("# Bar Directory Recon - Complete Documentation")
        merged_content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        merged_content.append(
            "This document consolidates all project documentation from multiple README files.\n"
        )

        # Table of contents
        merged_content.append(self.create_table_of_contents(files_metadata))
        merged_content.append("---\n")

        # Process each file
        for i, file_path in enumerate(readme_files):
            meta = files_metadata[i]
            print(f"Processing: {file_path.name}")

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                # Remove front matter if present
                content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

                # Adjust heading levels (make room for main h1)
                adjusted_content = self.adjust_heading_levels(content, base_level=2)

                # Add section header
                merged_content.append(f"## {meta['title']}")
                merged_content.append(
                    f"*Source: `{meta['filename']}` | Phase: {meta['phase']} | Date: {meta['date']}*\n"
                )

                # Add content
                merged_content.append(adjusted_content)
                merged_content.append("\n---\n")

            except Exception as e:
                print(f"Warning: Could not process {file_path.name}: {e}")
                merged_content.append(f"## {meta['title']} (Error)")
                merged_content.append(f"*Could not process file: {e}*\n")
                merged_content.append("---\n")

        # Add footer
        merged_content.append("## Document Information")
        merged_content.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        merged_content.append(f"- **Source Files**: {len(readme_files)} README files")
        merged_content.append("- **Project**: Bar Directory Recon")
        merged_content.append(
            "- **Repository**: [bar-directory-recon](https://github.com/samiat-quadir/bar-directory-recon)"
        )

        # Write merged file
        final_content = "\n".join(merged_content)
        output_path.write_text(final_content, encoding="utf-8")

        print("\n✅ Documentation merged successfully!")
        print(f"📄 Output: {output_path}")
        print(f"📊 Size: {len(final_content):,} characters")

        return output_path

    def create_index_files(self):
        """Create additional index files for different purposes."""
        # Create API reference index
        api_files = list(self.project_root.glob("**/API*.md"))
        if api_files:
            self._create_api_index(api_files)

        # Create setup guide index
        setup_files = list(self.project_root.glob("**/*SETUP*.md"))
        setup_files.extend(self.project_root.glob("**/*GUIDE*.md"))
        if setup_files:
            self._create_setup_index(setup_files)

    def _create_api_index(self, api_files: list[Path]):
        """Create API documentation index."""
        content = ["# API Reference\n"]
        for file_path in sorted(api_files):
            content.append(f"## {file_path.stem}")
            content.append(f"[View Documentation]({file_path.relative_to(self.docs_dir)})\n")

        (self.docs_dir / "API.md").write_text("\n".join(content))

    def _create_setup_index(self, setup_files: list[Path]):
        """Create setup/guide documentation index."""
        content = ["# Setup and Configuration Guides\n"]
        for file_path in sorted(setup_files):
            content.append(f"## {file_path.stem}")
            content.append(f"[View Guide]({file_path.relative_to(self.docs_dir)})\n")

        (self.docs_dir / "SETUP.md").write_text("\n".join(content))


def main():
    """Main entry point for documentation merger."""
    parser = argparse.ArgumentParser(description="Merge README files into unified documentation")
    parser.add_argument(
        "--project-root", type=Path, default=".", help="Root directory of the project"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: docs/README.md)",
    )
    parser.add_argument(
        "--create-indexes", action="store_true", help="Create additional index files"
    )

    args = parser.parse_args()

    merger = DocumentationMerger(args.project_root)

    # Merge main documentation
    output_path = merger.merge_files(args.output)

    # Create index files if requested
    if args.create_indexes:
        merger.create_index_files()
        print("📚 Additional index files created")

    print("\n🎉 Documentation consolidation complete!")
    print(f"📖 View merged docs: {output_path}")


if __name__ == "__main__":
    main()
