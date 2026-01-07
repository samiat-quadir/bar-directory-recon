#!/usr/bin/env python3
"""
Complete Installation Verification for Unified Scraping Framework
Checks all required dependencies, tools, and system requirements.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Python Version Check")
    print("=" * 50)
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name} ({version})")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_system_tools():
    """Check system tools availability."""
    print("\n🔧 System Tools Check")
    print("=" * 50)

    tools = {
        'git': 'git --version',
        'chrome': 'where chrome.exe',
        'powershell': 'powershell -Command "Get-Host | Select-Object Version"'
    }

    results = {}
    for tool, command in tools.items():
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0 or (tool == 'chrome' and 'Program Files' in result.stderr):
                print(f"✅ {tool} - Available")
                results[tool] = True
            else:
                print(f"❌ {tool} - Not available")
                results[tool] = False
        except Exception as e:
            print(f"❌ {tool} - Error checking: {e}")
            results[tool] = False

    return results

def check_core_dependencies():
    """Check core project dependencies."""
    print("\n📦 Core Dependencies Check")
    print("=" * 50)

    core_packages = [
        ('selenium', 'selenium'),
        ('webdriver-manager', 'webdriver_manager'),
        ('beautifulsoup4', 'bs4'),
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('openpyxl', 'openpyxl'),
        ('python-dotenv', 'dotenv'),
        ('typer', 'typer'),
        ('lxml', 'lxml'),
        ('pillow', 'PIL')
    ]

    results = []
    for package, import_name in core_packages:
        results.append(check_package(package, import_name))

    return all(results)

def check_notification_dependencies():
    """Check notification dependencies."""
    print("\n📧 Notification Dependencies Check")
    print("=" * 50)

    notification_packages = [
        ('twilio', 'twilio'),
        ('requests', 'requests')
    ]

    results = []
    for package, import_name in notification_packages:
        results.append(check_package(package, import_name))

    return all(results)

def check_google_sheets_dependencies():
    """Check Google Sheets dependencies."""
    print("\n📊 Google Sheets Dependencies Check")
    print("=" * 50)

    google_packages = [
        ('google-auth', 'google.auth'),
        ('google-auth-oauthlib', 'google_auth_oauthlib'),
        ('google-auth-httplib2', 'google_auth_httplib2'),
        ('google-api-python-client', 'googleapiclient'),
        ('gspread', 'gspread')
    ]

    results = []
    for package, import_name in google_packages:
        results.append(check_package(package, import_name))

    return all(results)

def check_development_tools():
    """Check development tools."""
    print("\n🛠️ Development Tools Check")
    print("=" * 50)

    dev_packages = [
        ('pytest', 'pytest'),
        ('black', 'black'),
        ('isort', 'isort'),
        ('mypy', 'mypy'),
        ('flake8', 'flake8'),
        ('bandit', 'bandit'),
        ('pre-commit', 'pre_commit')
    ]

    results = []
    for package, import_name in dev_packages:
        results.append(check_package(package, import_name))

    return all(results)

def check_framework_modules():
    """Check framework modules."""
    print("\n🏗️ Framework Modules Check")
    print("=" * 50)

    modules = [
        'src.config_loader',
        'src.webdriver_manager',
        'src.data_extractor',
        'src.pagination_manager',
        'src.orchestrator',
        'src.unified_schema',
        'src.notification_agent',
        'src.security_audit',
        'src.logger'
    ]

    results = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {module} - {e}")
            results.append(False)

    return all(results)

def check_configuration_files():
    """Check configuration files."""
    print("\n📋 Configuration Files Check")
    print("=" * 50)

    config_files = [
        'config/lawyer_directory.json',
        'config/realtor_directory.json',
        'unified_scraper.py',
        'DEPLOYMENT_GUIDE.md',
        'requirements.txt'
    ]

    results = []
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            results.append(True)
        else:
            print(f"❌ {file_path} - Missing")
            results.append(False)

    return all(results)

def main():
    """Main installation check."""
    print("🔍 Complete Installation Verification")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version()),
        ("System Tools", all(check_system_tools().values())),
        ("Core Dependencies", check_core_dependencies()),
        ("Notification Dependencies", check_notification_dependencies()),
        ("Google Sheets Dependencies", check_google_sheets_dependencies()),
        ("Development Tools", check_development_tools()),
        ("Framework Modules", check_framework_modules()),
        ("Configuration Files", check_configuration_files())
    ]

    print("\n" + "=" * 60)
    print("📋 Installation Summary")
    print("=" * 60)

    passed = 0
    total = len(checks)

    for check_name, result in checks:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name:<30} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Framework is ready for production.")
        print("\n📚 Next Steps:")
        print("1. Configure credentials (see DEPLOYMENT_GUIDE.md)")
        print("2. Test with sample data")
        print("3. Set up automated scheduling")
        return True
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please install missing components.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
