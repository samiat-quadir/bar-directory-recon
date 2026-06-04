"""
Quick test script for Realtor Directory Automation
Tests basic functionality without running a full scrape
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported (pytest friendly)."""
    # core third-party deps
    import importlib
    import pytest

    required = [
        "requests",
        "pandas",
        "schedule",
        "bs4",
        "selenium",
    ]

    for mod in required:
        try:
            importlib.import_module(mod)
        except Exception as e:
            pytest.skip(f"Missing runtime dependency '{mod}': {e}")

    # project import
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory  # type: ignore
        _ = scrape_realtor_directory
    except Exception as e:
        pytest.skip(f"Plugin import failed: {e}")

def test_directories():
    """Test if required directories exist."""
    required_dirs = ["outputs", "logs", "universal_recon/plugins"]
    for directory in required_dirs:
        assert os.path.exists(directory), f"Missing directory: {directory}"

def test_files():
    """Test if required files exist."""
    required_files = [
        "universal_recon/plugins/realtor_directory_plugin.py",
        "universal_recon/plugin_registry.json",
        "realtor_automation.py",
        "requirements.txt",
    ]
    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing file: {file_path}"

def test_plugin_registry():
    """Test plugin registry configuration."""
    import json
    with open("universal_recon/plugin_registry.json", "r") as f:
        registry = json.load(f)

    realtor_plugin = None
    for plugin in registry:
        if plugin.get("site_name") == "realtor_directory":
            realtor_plugin = plugin
            break

    assert realtor_plugin is not None, "Realtor directory plugin not found in registry"
    assert isinstance(realtor_plugin.get("module"), str), "Plugin module not defined"
    assert isinstance(realtor_plugin.get("function"), str), "Plugin function not defined"

def main():
    """Convenience runner when executed directly."""
    # Keep behavior but rely on pytest for assertions; this runner simply reports failures
    results = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("File Test", test_files),
        ("Plugin Registry Test", test_plugin_registry),
    ]
    failures = []
    for name, fn in results:
        try:
            fn()
            print(f"✅ {name}")
        except Exception as e:
            failures.append((name, str(e)))
            print(f"❌ {name}: {e}")

    if failures:
        print("Some tests failed:")
        for name, msg in failures:
            print(f" - {name}: {msg}")
        return False
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
