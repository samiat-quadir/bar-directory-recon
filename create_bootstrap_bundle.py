#!/usr/bin/env python3
"""
Bootstrap Bundle Creator
Creates alienware_bootstrap_bundle.zip with all necessary bootstrap artifacts
"""

import os
import zipfile


def create_bootstrap_bundle():
    """Create the bootstrap bundle zip file."""

    # Define the files to include in the bundle
    files_to_bundle = [
        "bootstrap_alienware.ps1",
        "bootstrap_alienware.sh",
        ".env.template",
        "config/device_profile-Alienware.json",
        ".github/workflows/bootstrap-alienware.yml",
        "validate_alienware_bootstrap.py",
        "ALIENWARE_BOOTSTRAP_GUIDE.md",
        "ALIENWARE_BOOTSTRAP_IMPLEMENTATION_SUMMARY.md",
        "EXECUTION_CHECKLIST.md",
        "ENV_READY_REPORT.md",
        "requirements.txt",
        "requirements-core.txt",
        "requirements-optional.txt",
    ]

    bundle_path = "alienware_bootstrap_bundle.zip"

    print(f"Creating bootstrap bundle: {bundle_path}")

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_bundle:
            if os.path.exists(file_path):
                # Add file to zip, preserving directory structure
                zipf.write(file_path, file_path)
                print(f"✅ Added: {file_path}")
            else:
                print(f"❌ Missing: {file_path}")

    # Verify the bundle
    if os.path.exists(bundle_path):
        file_size = os.path.getsize(bundle_path) / 1024  # KB
        print(f"\n✅ Bundle created successfully!")
        print(f"📦 File: {bundle_path}")
        print(f"📏 Size: {file_size:.1f} KB")

        # List contents
        print(f"\n📋 Bundle Contents:")
        with zipfile.ZipFile(bundle_path, "r") as zipf:
            for info in zipf.infolist():
                print(f"   - {info.filename} ({info.file_size} bytes)")

        return True
    else:
        print("❌ Failed to create bundle")
        return False


if __name__ == "__main__":
    success = create_bootstrap_bundle()
    exit(0 if success else 1)
