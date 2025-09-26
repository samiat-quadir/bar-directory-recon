#!/usr/bin/env python3
"""
Archive Legacy Files - Phase 5 Cleanup
Move legacy scripts and modules to archive directory
"""

import shutil
from datetime import datetime
from pathlib import Path


def create_archive_manifest():
    """Create a manifest of what's being archived."""
    manifest_content = f"""# Legacy Files Archive Manifest
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Files Archived

### Legacy Batch Scripts
- usage_demo.py -> Replaced by unified CLI examples
- google_sheets_integration.py -> Integrated into orchestrator
- test_integration.bat -> Replaced by test framework
- RunRealtorAutomation.bat -> Replaced by unified CLI
- weekly_automation.bat -> Replaced by unified scheduler

### Legacy Tool Scripts
- tools/realtor_directory_scraper.py -> Replaced by unified framework

### Legacy Configuration Files
- Any orphaned config files not compatible with unified format

## Utility Functions Migrated

### From google_sheets_integration.py:
- Google Sheets authentication -> src/orchestrator.py
- Data export formatting -> src/unified_schema.py
- Duplicate detection logic -> src/unified_schema.py

### From realtor_directory_scraper.py:
- Contact info extraction patterns -> Integrated into unified data_extractor
- Data validation logic -> Integrated into unified schema validation

## Post-Archive Notes
- All functionality preserved in unified framework
- Legacy files kept for reference and emergency rollback
- Update automation scripts to use unified CLI
- Update documentation to reflect new structure
"""

    manifest_path = Path("archive/ARCHIVE_MANIFEST.md")
    manifest_path.write_text(manifest_content, encoding="utf-8")
    print(f"Created archive manifest: {manifest_path}")


def archive_file(source_path, archive_subdir="legacy_scripts"):
    """Archive a single file."""
    source = Path(source_path)
    if not source.exists():
        print(f"⚠️  File not found: {source_path}")
        return False

    archive_dir = Path("archive") / archive_subdir
    archive_dir.mkdir(parents=True, exist_ok=True)

    dest = archive_dir / source.name

    try:
        shutil.move(str(source), str(dest))
        print(f"✅ Archived: {source_path} -> {dest}")
        return True
    except Exception as e:
        print(f"❌ Failed to archive {source_path}: {e}")
        return False


def main():
    """Main archiving process."""
    print("🗂️  Starting Legacy Files Archive Process...")
    print("=" * 60)

    # Files to archive
    files_to_archive = [
        # Legacy Python modules
        ("usage_demo.py", "legacy_modules"),
        ("google_sheets_integration.py", "legacy_modules"),
        # Legacy batch scripts
        ("test_integration.bat", "legacy_scripts"),
        ("RunRealtorAutomation.bat", "legacy_scripts"),
        ("weekly_automation.bat", "legacy_scripts"),
        # Legacy tool scripts
        ("tools/realtor_directory_scraper.py", "legacy_modules"),
    ]

    # Archive files
    archived_count = 0
    for file_path, archive_subdir in files_to_archive:
        if archive_file(file_path, archive_subdir):
            archived_count += 1

    # Create manifest
    create_archive_manifest()

    print("=" * 60)
    print("🎉 Archive process complete!")
    print(f"📁 {archived_count} files archived")
    print("📋 Manifest created: archive/ARCHIVE_MANIFEST.md")
    print("\n⚠️  Remember to:")
    print("   - Update automation scripts to use unified CLI")
    print("   - Update documentation")
    print("   - Test unified framework functionality")


if __name__ == "__main__":
    main()
