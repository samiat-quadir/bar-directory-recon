#!/usr/bin/env python3
"""
Bootstrap Bundle Verification
============================
Final verification of the Alienware bootstrap bundle.
"""

import hashlib
import os
import zipfile


def verify_bootstrap_bundle():
    """Verify the bootstrap bundle is complete and valid."""

    bundle_path = "alienware_bootstrap_bundle.zip"

    print("🔍 BOOTSTRAP BUNDLE VERIFICATION")
    print("=" * 50)

    # Check if bundle exists
    if not os.path.exists(bundle_path):
        print("❌ Bundle not found!")
        return False

    # Get bundle info
    bundle_size = os.path.getsize(bundle_path)
    with open(bundle_path, "rb") as f:
        bundle_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"📦 Bundle: {bundle_path}")
    print(f"📏 Size: {bundle_size:,} bytes ({bundle_size/1024:.1f} KB)")
    print(f"🔐 SHA256: {bundle_hash}")

    # Verify ZIP integrity
    try:
        with zipfile.ZipFile(bundle_path, "r") as zipf:
            test_result = zipf.testzip()
            if test_result is None:
                print("✅ ZIP integrity: VALID")
            else:
                print(f"❌ ZIP integrity: CORRUPTED ({test_result})")
                return False
    except Exception as e:
        print(f"❌ ZIP error: {e}")
        return False

    # Check required files
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

    print("\n📋 Bundle Contents:")
    print("-" * 30)

    with zipfile.ZipFile(bundle_path, "r") as zipf:
        bundle_files = zipf.namelist()

        for required_file in required_files:
            if required_file in bundle_files:
                info = zipf.getinfo(required_file)
                print(f"✅ {required_file} ({info.file_size:,} bytes)")
            else:
                print(f"❌ {required_file} MISSING")
                return False

    print("\n📊 Bundle Summary:")
    print(f"   • Total Files: {len(bundle_files)}")
    print(f"   • Required Files: {len(required_files)}")
    print("   • All Present: ✅")
    print("   • ZIP Valid: ✅")
    print("   • Ready for Distribution: ✅")

    return True


if __name__ == "__main__":
    success = verify_bootstrap_bundle()
    print("\n" + "=" * 50)
    if success:
        print("🎉 BOOTSTRAP BUNDLE VERIFICATION: PASSED")
    else:
        print("❌ BOOTSTRAP BUNDLE VERIFICATION: FAILED")
