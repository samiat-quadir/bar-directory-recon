#!/usr/bin/env python3
"""
Dependency Verification Script
Check all dependencies for the unified scraping framework
"""

import sys
import subprocess
from pathlib import Path

def check_dependency(package_name, import_name=None, optional=False):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name} - Available")
        return True
    except ImportError:
        status = "⚠️  OPTIONAL" if optional else "❌ REQUIRED"
        print(f"{status} {package_name} - Not available")
        return not optional

def check_core_dependencies():
    """Check core framework dependencies."""
    print("🔍 Checking Core Dependencies...")
    print("=" * 50)

    core_deps = [
        ("selenium", "selenium"),
        ("webdriver-manager", "webdriver_manager"),
        ("beautifulsoup4", "bs4"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("openpyxl", "openpyxl"),
        ("python-dotenv", "dotenv"),
        ("typer", "typer"),
    ]

    all_available = True
    for package, import_name in core_deps:
        if not check_dependency(package, import_name):
            all_available = False

    return all_available

def check_notification_dependencies():
    """Check notification system dependencies."""
    print("\n📧 Checking Notification Dependencies...")
    print("=" * 50)

    # These are optional but recommended
    notification_deps = [
        ("twilio", "twilio", True),  # SMS notifications
        ("requests", "requests", False),  # Slack webhooks (required anyway)
    ]

    results = {}
    for package, import_name, optional in notification_deps:
        results[package] = check_dependency(package, import_name, optional)

    return results

def check_google_sheets_dependencies():
    """Check Google Sheets integration dependencies."""
    print("\n📊 Checking Google Sheets Dependencies...")
    print("=" * 50)

    # These are optional for Google Sheets integration
    sheets_deps = [
        ("google-auth", "google.auth", True),
        ("google-auth-oauthlib", "google_auth_oauthlib", True),
        ("google-auth-httplib2", "google.auth.transport.requests", True),
        ("google-api-python-client", "googleapiclient", True),
    ]

    results = {}
    for package, import_name, optional in sheets_deps:
        results[package] = check_dependency(package, import_name, optional)

    return results

def check_framework_modules():
    """Check if framework modules can be imported."""
    print("\n🏗️ Checking Framework Modules...")
    print("=" * 50)

    framework_modules = [
        ("src.config_loader", "ConfigLoader"),
        ("src.webdriver_manager", "WebDriverManager"),
        ("src.data_extractor", "DataExtractor"),
        ("src.pagination_manager", "PaginationManager"),
        ("src.orchestrator", "ScrapingOrchestrator"),
        ("src.unified_schema", "SchemaMapper"),
        ("src.notification_agent", "NotificationAgent"),
        ("src.security_audit", "SecurityAuditor"),
    ]

    all_available = True
    for module_path, class_name in framework_modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_path}.{class_name} - Available")
        except (ImportError, AttributeError) as e:
            print(f"❌ {module_path}.{class_name} - Error: {e}")
            all_available = False

    return all_available

def suggest_installations(missing_packages):
    """Suggest installation commands for missing packages."""
    if not missing_packages:
        return

    print("\n💡 Installation Suggestions:")
    print("=" * 50)

    # Core packages
    core_missing = [pkg for pkg in missing_packages if pkg in [
        'selenium', 'webdriver-manager', 'beautifulsoup4', 'pandas',
        'requests', 'openpyxl', 'python-dotenv', 'typer'
    ]]

    if core_missing:
        print("For core functionality:")
        print(f"pip install {' '.join(core_missing)}")

    # Google Sheets packages
    sheets_missing = [pkg for pkg in missing_packages if pkg.startswith('google-')]
    if sheets_missing:
        print("\nFor Google Sheets integration:")
        print(f"pip install {' '.join(sheets_missing)}")

    # Notification packages
    if 'twilio' in missing_packages:
        print("\nFor SMS notifications:")
        print("pip install twilio")

    print("\nOr install all optional dependencies:")
    print("pip install -r requirements.txt")

def main():
    """Main verification process."""
    print("🔍 Unified Scraping Framework - Dependency Verification")
    print("=" * 60)

    missing_packages = []

    # Check core dependencies
    if not check_core_dependencies():
        missing_packages.extend(['selenium', 'webdriver-manager', 'beautifulsoup4',
                                'pandas', 'requests', 'openpyxl', 'python-dotenv', 'typer'])

    # Check notification dependencies
    notification_results = check_notification_dependencies()
    if not notification_results.get('twilio', True):
        missing_packages.append('twilio')

    # Check Google Sheets dependencies
    sheets_results = check_google_sheets_dependencies()
    for package, available in sheets_results.items():
        if not available:
            missing_packages.append(package)

    # Check framework modules
    framework_available = check_framework_modules()

    # Summary
    print("\n📋 Verification Summary:")
    print("=" * 60)

    if framework_available and not missing_packages:
        print("🎉 All dependencies are available!")
        print("✅ Framework is ready for production use.")
    else:
        if missing_packages:
            print(f"⚠️  Missing {len(missing_packages)} optional dependencies")
        if not framework_available:
            print("❌ Some framework modules have issues")

        suggest_installations(missing_packages)

    print("\n📚 Next Steps:")
    print("1. Install any missing dependencies")
    print("2. Configure credentials (see DEPLOYMENT_GUIDE.md)")
    print("3. Test the framework with sample data")
    print("4. Set up automated scheduling")

if __name__ == "__main__":
    main()
