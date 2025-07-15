#!/usr/bin/env python3
"""
Installation Check and Setup Script

This script verifies that all required dependencies are installed
and provides guidance for setting up the enhanced configuration system.
"""

import subprocess
import sys
from pathlib import Path


def check_dependency(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name.split("[")[0]  # Handle pydantic[email]

    try:
        __import__(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)


def install_core_dependencies():
    """Install core dependencies."""
    print("📦 Installing core dependencies...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-core.txt"])
        print("✅ Core dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def main():
    """Main setup and check function."""
    print("🔧 Configuration System Setup Check")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("automation").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (The directory containing the 'automation' folder)")
        sys.exit(1)

    print("📍 Project directory: ✅")

    # Check core dependencies
    required_packages = [
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv"),
        ("pyyaml", "yaml"),
        ("jinja2", "jinja2"),
        ("email-validator", "email_validator"),
    ]

    missing_packages = []

    print("\n📋 Checking dependencies...")
    for package, import_name in required_packages:
        is_installed, error = check_dependency(package, import_name)
        if is_installed:
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} - {error}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")

        user_input = input("\nWould you like to install missing dependencies now? (y/n): ")
        if user_input.lower() in ("y", "yes"):
            if install_core_dependencies():
                print("\n✅ All dependencies installed!")
            else:
                print("\n❌ Installation failed. Please install manually:")
                print("   pip install -r requirements-core.txt")
                sys.exit(1)
        else:
            print("Please install dependencies manually:")
            print("   pip install -r requirements-core.txt")
            sys.exit(1)
    else:
        print("\n✅ All dependencies are installed!")

    # Test imports
    print("\n🧪 Testing imports...")
    try:
        from automation.config_models import AutomationConfig  # noqa: F401
        from automation.enhanced_config_loader import ConfigLoader  # noqa: F401
        from automation.enhanced_dashboard import EnhancedDashboardManager  # noqa: F401

        print("   ✅ All imports successful!")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        sys.exit(1)

    # Check file structure
    print("\n📁 Checking file structure...")
    required_files = [
        "automation/config_models.py",
        "automation/enhanced_config_loader.py",
        "automation/enhanced_dashboard.py",
        "automation/templates/dashboard.html",
        "requirements-core.txt",
        "requirements-optional.txt",
    ]

    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_files_exist = False

    if not all_files_exist:
        print("\n❌ Some required files are missing!")
        sys.exit(1)

    # Final check
    print("\n🎉 Setup check completed successfully!")
    print("\nNext steps:")
    print("1. Run the demo: python configuration_demo.py")
    print("2. Generate config templates:")
    print(
        '   python -c "from automation.enhanced_config_loader import '
        + "generate_config_template; generate_config_template('automation')\""
    )
    print("3. Set up your .env file for secure configuration")
    print("4. Customize your configuration files")

    print("\n📚 Documentation:")
    print("- Configuration models: automation/config_models.py")
    print("- Implementation summary: PHASE1_IMPLEMENTATION_SUMMARY.md")


if __name__ == "__main__":
    main()
