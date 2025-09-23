#!/usr/bin/env python3
"""
Environment State Validation
============================

Validates the current environment state and checks for missing dependencies
or configuration mismatches across devices.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def check_python_packages() -> Tuple[List[str], List[str]]:
    """Check installed Python packages against requirements."""
    print("🔍 Checking Python packages...")

    # Read requirements
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return [], []

    # Parse requirements
    required_packages = []
    with open(req_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # Extract package name (before >= or ==)
                package = line.split(">=")[0].split("==")[0].split("[")[0].strip()
                if package:
                    required_packages.append(package)

    # Get installed packages
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True, check=True
        , timeout=60)
        installed_data = json.loads(result.stdout)
        installed_packages = {pkg["name"].lower().replace("-", "_"): pkg["version"] for pkg in installed_data}
    except Exception as e:
        print(f"❌ Failed to get installed packages: {e}")
        return [], []

    # Check for missing packages
    missing = []
    present = []

    for req_pkg in required_packages:
        # Normalize package name for comparison
        normalized_req = req_pkg.lower().replace("-", "_")

        # Check various name formats
        found = False
        for installed_name in installed_packages.keys():
            if (
                normalized_req == installed_name
                or normalized_req == installed_name.replace("_", "-")
                or req_pkg.lower() == installed_name
            ):
                present.append(f"{req_pkg} ({installed_packages[installed_name]})")
                found = True
                break

        if not found:
            missing.append(req_pkg)

    return missing, present


def check_configuration_files() -> Dict[str, bool]:
    """Check for required configuration files."""
    print("🔍 Checking configuration files...")

    config_checks = {}

    # Required config files
    required_configs = ["config/device_profile.json", ".env", ".venv/pyvenv.cfg", "automation/config.yaml"]

    for config_path in required_configs:
        path = Path(config_path)
        config_checks[config_path] = path.exists()

    # Check for device-specific configs
    import platform

    device_name = platform.node()
    device_config = f"config/device_profile-{device_name}.json"
    config_checks[device_config] = Path(device_config).exists()

    return config_checks


def check_directory_structure() -> Dict[str, bool]:
    """Check for required directories."""
    print("🔍 Checking directory structure...")

    required_dirs = [
        "logs",
        "logs/automation",
        "logs/device_logs",
        "output",
        "input",
        "config",
        "automation",
        "tools",
        ".venv",
        "scripts",
    ]

    dir_checks = {}
    for dir_path in required_dirs:
        path = Path(dir_path)
        dir_checks[dir_path] = path.exists() and path.is_dir()

    return dir_checks


def check_external_tools() -> Dict[str, bool]:
    """Check for external tools and commands."""
    print("🔍 Checking external tools...")

    tools = {
        "git": ["git", "--version"],
        "pre-commit": ["pre-commit", "--version"],
        "chrome/chromium": None,  # Special check
    }

    tool_checks = {}

    for tool, cmd in tools.items():
        if cmd is None:
            # Special handling for Chrome
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
            ]
            tool_checks[tool] = any(Path(p).exists() for p in chrome_paths)
        else:
            try:
                subprocess.run(cmd, capture_output=True, check=True, timeout=60)
                tool_checks[tool] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                tool_checks[tool] = False

    return tool_checks


def check_environment_variables() -> Dict[str, Optional[str]]:
    """Check important environment variables."""
    print("🔍 Checking environment variables...")

    important_vars = ["PYTHONPATH", "PATH", "VIRTUAL_ENV", "PROJECT_ROOT", "ONEDRIVE_PATH"]

    env_checks = {}
    for var in important_vars:
        env_checks[var] = os.environ.get(var)

    return env_checks


def generate_validation_report():
    """Generate comprehensive validation report."""
    print("=" * 80)
    print("🔍 ENVIRONMENT VALIDATION REPORT")
    print("=" * 80)
    print(f"Device: {os.environ.get('COMPUTERNAME', 'Unknown')}")
    print(f"User: {os.environ.get('USERNAME', 'Unknown')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 80)

    # 1. Python Packages
    print("\n📦 PYTHON PACKAGES")
    print("-" * 40)
    missing_packages, present_packages = check_python_packages()

    if missing_packages:
        print(f"❌ Missing packages ({len(missing_packages)}):")
        for pkg in missing_packages:
            print(f"   - {pkg}")
    else:
        print("✅ All required packages are installed")

    print(f"\n✅ Installed packages ({len(present_packages)} checked):")
    for pkg in present_packages[:10]:  # Show first 10
        print(f"   - {pkg}")
    if len(present_packages) > 10:
        print(f"   ... and {len(present_packages) - 10} more")

    # 2. Configuration Files
    print("\n⚙️ CONFIGURATION FILES")
    print("-" * 40)
    config_checks = check_configuration_files()

    for config, exists in config_checks.items():
        status = "✅" if exists else "❌"
        print(f"{status} {config}")

    # 3. Directory Structure
    print("\n📁 DIRECTORY STRUCTURE")
    print("-" * 40)
    dir_checks = check_directory_structure()

    for directory, exists in dir_checks.items():
        status = "✅" if exists else "❌"
        print(f"{status} {directory}/")

    # 4. External Tools
    print("\n🛠️ EXTERNAL TOOLS")
    print("-" * 40)
    tool_checks = check_external_tools()

    for tool, available in tool_checks.items():
        status = "✅" if available else "❌"
        print(f"{status} {tool}")

    # 5. Environment Variables
    print("\n🌍 ENVIRONMENT VARIABLES")
    print("-" * 40)
    env_checks = check_environment_variables()

    for var, value in env_checks.items():
        if value:
            print(f"✅ {var} = {value[:50]}..." if len(str(value)) > 50 else f"✅ {var} = {value}")
        else:
            print(f"❌ {var} = (not set)")

    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)

    total_issues = 0

    if missing_packages:
        total_issues += len(missing_packages)
        print(f"❌ Missing packages: {len(missing_packages)}")

    missing_configs = sum(1 for exists in config_checks.values() if not exists)
    if missing_configs:
        total_issues += missing_configs
        print(f"❌ Missing config files: {missing_configs}")

    missing_dirs = sum(1 for exists in dir_checks.values() if not exists)
    if missing_dirs:
        total_issues += missing_dirs
        print(f"❌ Missing directories: {missing_dirs}")

    missing_tools = sum(1 for available in tool_checks.values() if not available)
    if missing_tools:
        total_issues += missing_tools
        print(f"❌ Missing tools: {missing_tools}")

    missing_env_vars = sum(1 for value in env_checks.values() if not value)
    if missing_env_vars:
        print(f"⚠️ Missing environment variables: {missing_env_vars}")

    if total_issues == 0:
        print("✅ Environment validation PASSED - No critical issues found!")
    else:
        print(f"❌ Environment validation FAILED - {total_issues} issues found")
        print("\n🛠️ NEXT STEPS:")
        if missing_packages:
            print("1. Install missing packages: pip install -r requirements.txt")
        if missing_configs:
            print("2. Create missing configuration files")
        if missing_dirs:
            print("3. Create missing directories")
        if missing_tools:
            print("4. Install missing external tools")

    return total_issues == 0


if __name__ == "__main__":
    success = generate_validation_report()
    sys.exit(0 if success else 1)

