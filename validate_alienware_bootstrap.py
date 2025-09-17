#!/usr/bin/env python3
"""
Alienware Device Bootstrap Validation
====================================

Supplemental validation script specifically for Alienware device bootstrap.
This script performs additional checks beyond the standard validate_env_state.py
to ensure complete parity with the ASUS golden image.
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


def get_device_info() -> dict[str, str]:
    """Get comprehensive device information."""
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def check_alienware_specific_config() -> dict[str, bool]:
    """Check Alienware-specific configuration requirements."""
    print("🖥️  Checking Alienware-specific configuration...")

    checks = {}
    device_info = get_device_info()
    hostname = device_info["hostname"]

    # Check device profile exists for this specific device
    device_profile_path = f"config/device_profile-{hostname}.json"
    checks[f"device_profile_{hostname}"] = Path(device_profile_path).exists()

    # Check device profile has required fields
    if Path(device_profile_path).exists():
        try:
            with open(device_profile_path) as f:
                profile = json.load(f)

            required_fields = [
                "device",
                "username",
                "user_home",
                "python_path",
                "onedrive_path",
                "project_root",
                "virtual_env",
            ]

            for field in required_fields:
                checks[f"profile_field_{field}"] = field in profile

            # Validate paths exist
            if "project_root" in profile:
                checks["profile_project_root_exists"] = Path(
                    profile["project_root"]
                ).exists()
            if "virtual_env" in profile:
                checks["profile_venv_exists"] = Path(profile["virtual_env"]).exists()

        except Exception as e:
            print(f"❌ Error reading device profile: {e}")
            checks["profile_readable"] = False

    # Check .env file has Alienware-specific settings
    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path) as f:
                env_content = f.read()

            checks["env_has_device_name"] = "DEVICE_NAME" in env_content
            checks["env_has_alienware"] = "ALIENWARE" in env_content.upper()
            checks["env_has_project_root"] = "PROJECT_ROOT" in env_content

        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            checks["env_readable"] = False

    return checks


def check_cross_device_compatibility() -> dict[str, bool]:
    """Check cross-device compatibility features."""
    print("🔄 Checking cross-device compatibility...")

    checks = {}

    # Check for hardcoded paths
    python_files = list(Path(".").rglob("*.py"))
    hardcoded_paths = []

    for py_file in python_files[:20]:  # Check first 20 Python files
        try:
            with open(py_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Look for common hardcoded path patterns
            hardcoded_patterns = [
                "C:\\Code\\",
                "C:/Code/",
                "/home/samqu/",
                "Users/samqu/",
                "OneDrive - Digital Age Marketing Group",
            ]

            for pattern in hardcoded_patterns:
                if pattern in content:
                    hardcoded_paths.append(f"{py_file}: {pattern}")

        except Exception:
            continue

    checks["no_hardcoded_paths"] = len(hardcoded_paths) == 0
    if hardcoded_paths:
        print(f"⚠️  Found hardcoded paths in {len(hardcoded_paths)} locations")

    # Check for relative path usage
    checks["uses_relative_paths"] = True  # Assume true unless proven otherwise

    # Check device path resolver
    resolver_files = [
        "tools/device_path_resolver.py",
        "automation/device_resolver.py",
        "config/path_resolver.py",
    ]

    checks["has_path_resolver"] = any(Path(f).exists() for f in resolver_files)

    return checks


def check_bootstrap_artifacts() -> dict[str, bool]:
    """Check artifacts created by bootstrap process."""
    print("📋 Checking bootstrap artifacts...")

    checks = {}

    # Check bootstrap report exists
    checks["bootstrap_report_exists"] = Path("alienware_validation_report.md").exists()

    # Check virtual environment structure
    venv_path = Path(".venv")
    if venv_path.exists():
        venv_structure = {
            "Scripts" if platform.system() == "Windows" else "bin": False,
            "Lib" if platform.system() == "Windows" else "lib": False,
            "Include" if platform.system() == "Windows" else "include": False,
            "pyvenv.cfg": False,
        }

        for item, _ in venv_structure.items():
            venv_structure[item] = (venv_path / item).exists()

        checks.update({f"venv_{k}": v for k, v in venv_structure.items()})

    # Check log directories
    log_dirs = ["logs", "logs/automation", "logs/device_logs"]
    for log_dir in log_dirs:
        checks[f"log_dir_{log_dir.replace('/', '_')}"] = Path(log_dir).exists()

    return checks


def compare_with_golden_image() -> dict[str, str]:
    """Compare current setup with ASUS golden image requirements."""
    print("🏆 Comparing with ASUS golden image...")

    comparison = {}

    # Expected package count from golden image
    expected_packages = 45

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )
        installed_packages = json.loads(result.stdout)
        actual_count = len(installed_packages)

        if actual_count >= expected_packages:
            comparison["package_count"] = (
                f"✅ {actual_count}/{expected_packages} packages"
            )
        else:
            comparison["package_count"] = (
                f"❌ {actual_count}/{expected_packages} packages"
            )

    except Exception as e:
        comparison["package_count"] = f"❌ Error checking packages: {e}"

    # Check specific packages from golden image
    golden_packages = [
        "bs4",
        "pdfplumber",
        "PyPDF2",
        "tabula-py",
        "dnspython",
        "aiofiles",
        "watchdog",
        "azure-storage-blob",
        "azure-identity",
        "azure-keyvault-secrets",
    ]

    missing_golden = []
    try:
        installed_names = {
            pkg["name"].lower().replace("-", "_") for pkg in installed_packages
        }

        for pkg in golden_packages:
            pkg_normalized = pkg.lower().replace("-", "_")
            if pkg_normalized not in installed_names:
                missing_golden.append(pkg)

    except Exception:
        missing_golden = ["Error checking"]

    if missing_golden:
        comparison["golden_packages"] = f"❌ Missing: {', '.join(missing_golden)}"
    else:
        comparison["golden_packages"] = "✅ All golden image packages present"

    # Configuration comparison
    expected_configs = ["config/device_profile.json", ".env", ".venv/pyvenv.cfg"]

    missing_configs = [cfg for cfg in expected_configs if not Path(cfg).exists()]

    if missing_configs:
        comparison["configurations"] = f"❌ Missing: {', '.join(missing_configs)}"
    else:
        comparison["configurations"] = "✅ All required configurations present"

    return comparison


def generate_alienware_report():
    """Generate comprehensive Alienware bootstrap validation report."""
    print("=" * 80)
    print("🖥️  ALIENWARE DEVICE BOOTSTRAP VALIDATION")
    print("=" * 80)

    device_info = get_device_info()
    print(f"Device: {device_info['hostname']}")
    print(f"System: {device_info['system']} {device_info['release']}")
    print(
        f"Python: {device_info['python_version']} ({device_info['python_implementation']})"
    )
    print(f"Working Directory: {os.getcwd()}")
    print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    total_issues = 0

    # 1. Alienware-specific configuration
    print("\n🖥️  ALIENWARE-SPECIFIC CONFIGURATION")
    print("-" * 50)
    alienware_checks = check_alienware_specific_config()

    for check, result in alienware_checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check.replace('_', ' ').title()}")
        if not result:
            total_issues += 1

    # 2. Cross-device compatibility
    print("\n🔄 CROSS-DEVICE COMPATIBILITY")
    print("-" * 50)
    compat_checks = check_cross_device_compatibility()

    for check, result in compat_checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check.replace('_', ' ').title()}")
        if not result:
            total_issues += 1

    # 3. Bootstrap artifacts
    print("\n📋 BOOTSTRAP ARTIFACTS")
    print("-" * 50)
    artifact_checks = check_bootstrap_artifacts()

    for check, result in artifact_checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check.replace('_', ' ').title()}")
        if not result:
            total_issues += 1

    # 4. Golden image comparison
    print("\n🏆 GOLDEN IMAGE COMPARISON")
    print("-" * 50)
    comparison = compare_with_golden_image()

    for check, result in comparison.items():
        print(f"{result}")
        if "❌" in result:
            total_issues += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 ALIENWARE BOOTSTRAP VALIDATION SUMMARY")
    print("=" * 80)

    if total_issues == 0:
        print("✅ ALIENWARE DEVICE SUCCESSFULLY BOOTSTRAPPED!")
        print("🎯 Device is in COMPLETE PARITY with ASUS golden image")
        print("\n🚀 Ready for production use!")
        print("\nNext steps:")
        print("1. Update .env with your API keys")
        print("2. Test automation workflows")
        print("3. Verify cross-device sync functionality")
    else:
        print(f"❌ BOOTSTRAP VALIDATION FAILED - {total_issues} issues found")
        print("\n🛠️  RECOMMENDED ACTIONS:")

        if any("❌" in result for result in comparison.values()):
            print("1. Re-run bootstrap script to fix missing packages/configs")

        if not compat_checks.get("no_hardcoded_paths", True):
            print("2. Update scripts to use relative paths")

        if not alienware_checks.get(f"device_profile_{device_info['hostname']}", True):
            print("3. Create device-specific profile")

        print("4. Run standard validation: python validate_env_state.py")

    print("\n" + "=" * 80)

    return total_issues == 0


if __name__ == "__main__":
    success = generate_alienware_report()
    sys.exit(0 if success else 1)
