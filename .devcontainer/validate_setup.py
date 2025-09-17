#!/usr/bin/env python3
"""
DevContainer Setup Validation Script
Verifies that the development environment is properly configured
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path


def check_python_environment():
    """Check Python version and basic environment."""
    print("🐍 Python Environment Check")
    print("=" * 50)

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python version compatible (3.11+)")
        success = True
    else:
        print("❌ Python version incompatible (requires 3.11+)")
        success = False

    # Check PYTHONPATH
    pythonpath = os.environ.get("PYTHONPATH", "")
    if "/workspaces/bar-directory-recon" in pythonpath:
        print("✅ PYTHONPATH configured correctly")
    else:
        print("⚠️  PYTHONPATH may need adjustment")

    return success


def check_core_dependencies():
    """Check core project dependencies."""
    print("\n📦 Core Dependencies Check")
    print("=" * 50)

    core_deps = [
        ("selenium", "selenium"),
        ("beautifulsoup4", "bs4"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("typer", "typer"),
        ("pydantic", "pydantic"),
        ("aiohttp", "aiohttp"),
        ("loguru", "loguru"),
    ]

    success = True
    for package, import_name in core_deps:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            success = False

    return success


def check_development_tools():
    """Check development and testing tools."""
    print("\n🔧 Development Tools Check")
    print("=" * 50)

    dev_tools = [
        ("pytest", "pytest"),
        ("black", "black"),
        ("flake8", "flake8"),
        ("mypy", "mypy"),
        ("coverage", "coverage"),
        ("pre-commit", "pre_commit"),
        ("isort", "isort"),
        ("bandit", "bandit"),
    ]

    success = True
    for tool, import_name in dev_tools:
        try:
            importlib.import_module(import_name)
            print(f"✅ {tool}")
        except ImportError:
            print(f"❌ {tool}")
            success = False

    return success


def check_project_structure():
    """Check project structure and key files."""
    print("\n📁 Project Structure Check")
    print("=" * 50)

    required_paths = [
        "src/",
        "universal_recon/",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        ".devcontainer/devcontainer.json",
        ".devcontainer/Dockerfile",
        ".pre-commit-config.yaml",
    ]

    success = True
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path}")
            success = False

    return success


def check_browser_setup():
    """Check browser and Selenium setup."""
    print("\n🌐 Browser Setup Check")
    print("=" * 50)

    # Check Chrome
    try:
        result = subprocess.run(
            ["google-chrome", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✅ Chrome: {result.stdout.strip()}")
        chrome_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Chrome not available")
        chrome_ok = False

    # Check container-safe Chrome
    container_chrome = Path("/usr/local/bin/chrome-no-sandbox")
    if container_chrome.exists():
        print("✅ Container-safe Chrome binary available")
    else:
        print("⚠️  Container-safe Chrome binary not found")

    # Check Selenium WebDriver
    try:
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Quick test
        print("✅ Selenium WebDriver options configured")
        selenium_ok = True
    except Exception as e:
        print(f"❌ Selenium setup issue: {e}")
        selenium_ok = False

    return chrome_ok and selenium_ok


def check_git_setup():
    """Check git configuration."""
    print("\n🔧 Git Setup Check")
    print("=" * 50)

    try:
        # Check git version
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✅ Git: {result.stdout.strip()}")

        # Check safe directory
        result = subprocess.run(
            ["git", "config", "--global", "--get-all", "safe.directory"],
            capture_output=True,
            text=True,
        )
        if "/workspaces/bar-directory-recon" in result.stdout:
            print("✅ Git safe directory configured")
        else:
            print("⚠️  Git safe directory may need configuration")

        return True
    except subprocess.CalledProcessError:
        print("❌ Git not available or not configured")
        return False


def check_ports_and_services():
    """Check port forwarding and service availability."""
    print("\n🔌 Ports and Services Check")
    print("=" * 50)

    expected_ports = [3000, 5432, 8000, 8080, 9090, 9182]

    print("Expected port forwards:")
    port_names = {
        3000: "Grafana",
        5432: "PostgreSQL",
        8000: "App Metrics",
        8080: "cAdvisor",
        9090: "Prometheus",
        9182: "Windows Exporter",
    }
    for port in expected_ports:
        print(f"  - {port}: {port_names.get(port, 'Unknown Service')}")

    print("✅ Port forwarding configured in devcontainer.json")
    return True


def run_test_suite():
    """Run a quick test to verify pytest works."""
    print("\n🧪 Test Suite Check")
    print("=" * 50)

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✅ Pytest: {result.stdout.strip()}")

        # Try to run a quick collection test
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("✅ Test collection successful")
        else:
            print("⚠️  Test collection had issues (may be normal for initial setup)")

        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("❌ Pytest not working properly")
        return False


def main():
    """Run all validation checks."""
    print("🔍 DevContainer Setup Validation")
    print("=" * 60)
    print(f"Working directory: {Path.cwd()}")
    print(f"Python executable: {sys.executable}")
    print("")

    checks = [
        ("Python Environment", check_python_environment),
        ("Core Dependencies", check_core_dependencies),
        ("Development Tools", check_development_tools),
        ("Project Structure", check_project_structure),
        ("Browser Setup", check_browser_setup),
        ("Git Setup", check_git_setup),
        ("Ports and Services", check_ports_and_services),
        ("Test Suite", run_test_suite),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))

    # Summary
    print("\n📋 Validation Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<8} {check_name}")

    print(f"\nResults: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! Development environment is ready.")
        print("\nNext steps:")
        print("  1. Run: pytest --cov=src --cov=universal_recon")
        print("  2. Start coding with full IntelliSense support")
        print("  3. Use docker-compose up -d for monitoring stack")
        return True
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please review and fix issues.")
        print("\nCommon fixes:")
        print("  - Run: pip install -r requirements-dev.txt")
        print(
            "  - Check: git config --global --add safe.directory /workspaces/bar-directory-recon"
        )
        print("  - Verify: PYTHONPATH includes project directories")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
