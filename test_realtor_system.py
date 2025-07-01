"""
Quick test script for Realtor Directory Automation
Tests basic functionality without running a full scrape
"""

import os
import sys
from pathlib import Path

def test_imports() -> bool:
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import requests
        _ = requests
        import pandas as pd  # type: ignore
        _ = pd
        import schedule
        _ = schedule
        from bs4 import BeautifulSoup
        _ = BeautifulSoup
        from selenium import webdriver
        _ = webdriver
    try:
        # Test project imports
        sys.path.insert(0, str(Path(__file__).parent))
        from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory
        _ = scrape_realtor_directory
        print("✅ Realtor plugin imported successfully")
    try:
        # Test project imports
        sys.path.insert(0, str(Path(__file__).parent))
        from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory
        print("✅ Realtor plugin imported successfully")
    except ImportError as e:
        print(f"❌ Plugin import error: {e}")
        return False
    
    return True

def test_directories() -> bool:
    """Test if required directories exist."""
    print("📁 Testing directories...")
    
    required_dirs = ["outputs", "logs", "universal_recon/plugins"]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Missing directory: {directory}")
            return False
    
    return True

def test_files() -> bool:
    """Test if required files exist."""
    print("📄 Testing required files...")
    
    required_files = [
        "universal_recon/plugins/realtor_directory_plugin.py",
        "universal_recon/plugin_registry.json",
        "realtor_automation.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    return True

def test_plugin_registry() -> bool:
    """Test plugin registry configuration."""
    print("🔧 Testing plugin registry...")
    
    try:
        import json
        with open("universal_recon/plugin_registry.json", "r") as f:
            registry = json.load(f)
        
        # Check for realtor directory plugin
        realtor_plugin = None
        for plugin in registry:
            if plugin.get("site_name") == "realtor_directory":
                realtor_plugin = plugin
                break
        
        if realtor_plugin:
            print("✅ Realtor directory plugin found in registry")
            print(f"   Module: {realtor_plugin.get('module')}")
            print(f"   Function: {realtor_plugin.get('function')}")
        else:
            print("❌ Realtor directory plugin not found in registry")
            return False
    
    except Exception as e:
        print(f"❌ Plugin registry error: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Realtor Directory Automation - System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("File Test", test_files),
        ("Plugin Registry Test", test_plugin_registry)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready for use.")
        print("\n🚀 Next steps:")
        print("1. Run 'python setup_realtor_automation.py' if you haven't already")
        print("2. Execute 'RunRealtorAutomation.bat' to start using the system")
        print("3. Try a test run: 'python realtor_automation.py --mode once --max-records 5'")
        return True
    else:
        print("❌ Some tests failed. Please check the setup and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
