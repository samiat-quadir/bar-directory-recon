#!/usr/bin/env python3
"""
Create Bootstrap Bundle for Alienware
=====================================
Creates the final bootstrap bundle with all required files.
"""

import os
import zipfile


def create_bootstrap_bundle():
    """Create the alienware bootstrap bundle with all required files."""

    # Required files for the bootstrap bundle
    required_files = [
        "bootstrap_alienware.ps1",
        "bootstrap_alienware.sh",
        ".env.template",
        "config/device_profile-Alienware.json",
        "validate_env_state.py",
        "validate_alienware_bootstrap.py",
        "alienware_playbook.ps1",
        "ENV_READY_REPORT.md",
    ]

    bundle_path = "alienware_bootstrap_bundle.zip"

    print("🔧 Creating Alienware Bootstrap Bundle...")
    print(f"📦 Bundle: {bundle_path}")
    print("=" * 50)

    # Remove existing bundle if it exists
    if os.path.exists(bundle_path):
        os.remove(bundle_path)
        print("🗑️  Removed existing bundle")

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in required_files:
            if os.path.exists(file_path):
                zipf.write(file_path, file_path)
                file_size = os.path.getsize(file_path)
                print(f"✅ Added: {file_path} ({file_size:,} bytes)")
            else:
                print(f"❌ Missing: {file_path}")

    # Get bundle info
    bundle_size = os.path.getsize(bundle_path)

    print("=" * 50)
    print(f"✅ Bundle created: {bundle_path}")
    print(f"📏 Bundle size: {bundle_size:,} bytes ({bundle_size/1024:.1f} KB)")

    # List contents for verification
    print("\n📋 Bundle Contents:")
    print("-" * 30)
    with zipfile.ZipFile(bundle_path, "r") as zipf:
        for info in zipf.infolist():
            print(f"  📄 {info.filename} ({info.file_size:,} bytes)")

    return bundle_path, bundle_size


if __name__ == "__main__":
    bundle_path, bundle_size = create_bootstrap_bundle()
