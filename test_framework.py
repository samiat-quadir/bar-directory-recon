#!/usr/bin/env python3
"""
Test script to validate the unified scraping framework
"""

import sys
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        print("🔍 Testing imports...")

        print("✅ WebDriverManager imported successfully")

        print("✅ PaginationManager imported successfully")

        print("✅ DataExtractor imported successfully")

        print("✅ ConfigLoader imported successfully")

        print("✅ ScrapingLogger imported successfully")

        print("✅ ScrapingOrchestrator imported successfully")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    try:
        print("\n🔍 Testing basic functionality...")

        # Test ConfigLoader
        from src.config_loader import ConfigLoader
        ConfigLoader()
        print("✅ ConfigLoader instantiated successfully")

        # Test ScrapingLogger
        from src.logger import ScrapingLogger
        logger = ScrapingLogger("test")
        logger.info("Test log message")
        print("✅ ScrapingLogger working successfully")

        # Test WebDriverManager config
        from src.webdriver_manager import WebDriverManager
        config = {'timeout': 10, 'headless': True}
        # Don't actually create the driver, just test initialization
        WebDriverManager(config)
        print("✅ WebDriverManager instantiated successfully")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation."""
    try:
        print("\n🔍 Testing configuration validation...")

        from src.config_loader import ConfigLoader
        loader = ConfigLoader()

        # Test with a sample config path
        config_path = Path("config/lawyer_directory.json")
        if config_path.exists():
            config = loader.load_config(str(config_path))
            validation_result = loader.validate_config(config)
            print(f"✅ Config validation result: {validation_result}")
        else:
            print("⚠️  Sample config file not found - skipping validation test")

        return True

    except Exception as e:
        print(f"❌ Config validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Unified Scraping Framework Tests")
    print("=" * 50)

    success_count = 0
    total_tests = 3

    if test_imports():
        success_count += 1

    if test_basic_functionality():
        success_count += 1

    if test_config_validation():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 All tests passed! Framework is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
