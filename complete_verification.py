#!/usr/bin/env python3
"""
Complete Installation Verification for Unified Scraping Framework
Check all dependencies, tools, and system requirements
"""

import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python Version...")
    print("=" * 40)

    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 8:
        print("✅ Python version compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_system_tools():
    """Check essential system tools."""
    print("\n🛠️ Checking System Tools...")
    print("=" * 40)

    tools = {
        'Git': 'git --version',
        'PowerShell': 'powershell -Command "Get-Host | Select-Object Version"'
    }

    available = []
    missing = []

    for tool, command in tools.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {tool} - Available")
                available.append(tool)
            else:
                print(f"❌ {tool} - Not working")
                missing.append(tool)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {tool} - Not found")
            missing.append(tool)

    return len(missing) == 0

def check_chrome_webdriver():
    """Check Chrome WebDriver availability."""
    print("\n🌐 Checking Chrome WebDriver...")
    print("=" * 40)

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver available at: {driver_path}")
        return True
    except Exception as e:
        print(f"❌ ChromeDriver issue: {e}")
        return False

def check_framework_functionality():
    """Test key framework functionality."""
    print("\n🏗️ Testing Framework Functionality...")
    print("=" * 40)

    tests = [
        ("Config Loader", "from src.config_loader import ConfigLoader; ConfigLoader()"),
        ("WebDriver Manager", "from src.webdriver_manager import WebDriverManager; WebDriverManager({})"),
        ("Data Extractor", "from src.data_extractor import DataExtractor; DataExtractor({})"),
        ("Orchestrator", "from src.orchestrator import ScrapingOrchestrator; ScrapingOrchestrator(None)"),
        ("Schema Mapper", "from src.unified_schema import SchemaMapper; SchemaMapper()"),
        ("Notification Agent", "from src.notification_agent import NotificationAgent; NotificationAgent()"),
        ("Security Auditor", "from src.security_audit import SecurityAuditor; SecurityAuditor()")
    ]

    all_working = True

    for test_name, test_code in tests:
        try:
            exec(test_code)
            print(f"✅ {test_name} - Working")
        except Exception as e:
            print(f"❌ {test_name} - Error: {e}")
            all_working = False

    return all_working

def check_cli_functionality():
    """Test CLI functionality."""
    print("\n💻 Testing CLI Functionality...")
    print("=" * 40)

    try:
        # Test CLI help
        result = subprocess.run([sys.executable, "unified_scraper.py", "--help"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and "usage:" in result.stdout.lower():
            print("✅ CLI help working")

            # Check for key commands
            if "scrape" in result.stdout and "notify-test" in result.stdout:
                print("✅ All CLI commands available")
                return True
            else:
                print("⚠️  Some CLI commands missing")
                return False
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def check_config_files():
    """Check configuration files."""
    print("\n📁 Checking Configuration Files...")
    print("=" * 40)

    config_files = [
        "config/lawyer_directory.json",
        "config/realtor_directory.json"
    ]

    all_present = True

    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file} - Present")
        else:
            print(f"❌ {config_file} - Missing")
            all_present = False

    return all_present

def check_output_directories():
    """Check and create output directories."""
    print("\n📂 Checking Output Directories...")
    print("=" * 40)

    directories = [
        "output",
        "logs",
        "logs/screenshots",
        "archive"
    ]

    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"✅ {directory}/ - Exists")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {directory}/ - Created")
            except Exception as e:
                print(f"❌ {directory}/ - Cannot create: {e}")

    return True

def generate_installation_report():
    """Generate final installation report."""
    print("\n📋 Installation Verification Report")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version()),
        ("System Tools", check_system_tools()),
        ("Chrome WebDriver", check_chrome_webdriver()),
        ("Framework Modules", check_framework_functionality()),
        ("CLI Functionality", check_cli_functionality()),
        ("Configuration Files", check_config_files()),
        ("Output Directories", check_output_directories())
    ]

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    print(f"\n📊 Results: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 INSTALLATION COMPLETE!")
        print("✅ All systems ready for production")
        print("\n🚀 Ready to:")
        print("   1. Configure credentials")
        print("   2. Test notifications")
        print("   3. Run first scraping session")
        print("   4. Set up automation")
    else:
        print("\n⚠️  Some issues found:")
        for check_name, result in checks:
            if not result:
                print(f"   ❌ {check_name}")

        print("\n💡 Next steps:")
        print("   1. Address the issues above")
        print("   2. Re-run this verification")
        print("   3. Check DEPLOYMENT_GUIDE.md for help")

    return passed == total

def main():
    """Main verification process."""
    print("🔍 Unified Scraping Framework - Complete Installation Verification")
    print("=" * 70)

    success = generate_installation_report()

    if success:
        print("\n📚 Quick Start Commands:")
        print("python unified_scraper.py --help")
        print("python unified_scraper.py scrape --config-dir config lawyer_directory --max-records 1 --verbose")
        print("python unified_scraper.py notify-test --config config/lawyer_directory.json --type all")

    return success

if __name__ == "__main__":
    main()
