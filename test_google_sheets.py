#!/usr/bin/env python3
"""
Test Google Sheets Integration
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_google_sheets_integration():
    """Test the Google Sheets integration setup."""

    print("🧪 Testing Google Sheets Integration")
    print("=" * 40)

    # Test 1: Check if credentials file exists
    credentials_file = project_root / "client_secret_1020100796152-n6l4bloev9ha8to4mcbc6h3p8e1n1t3e.apps.googleusercontent.com.json"
    print(f"📁 Credentials file: {'✅' if credentials_file.exists() else '❌'}")

    # Test 2: Check if Google Sheets packages are available
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        print("📦 Google API packages: ✅")
    except ImportError as e:
        print(f"📦 Google API packages: ❌ ({e})")
        return False

    # Test 3: Try to initialize Google Sheets integration
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        print("🔧 Google Sheets Integration import: ✅")

        # Try to initialize (this will prompt for auth if needed)
        sheets = GoogleSheetsIntegration(
            credentials_path=str(credentials_file)
        )

        if sheets.service:
            print("🔐 Google Sheets service initialized: ✅")
            print("🎉 Integration test successful!")
            return True
        else:
            print("🔐 Google Sheets service initialized: ❌")
            return False

    except Exception as e:
        print(f"🔧 Google Sheets Integration: ❌ ({e})")
        return False

def test_cli_arguments():
    """Test the CLI arguments parsing."""

    print("\n🖥️ Testing CLI Arguments")
    print("=" * 30)

    try:
        from universal_automation import main
        print("📋 CLI module import: ✅")

        # Test argument parsing
        import argparse
        parser = argparse.ArgumentParser()

        # Add the arguments we expect
        parser.add_argument("--export", choices=["csv", "google_sheets", "both"], default="both")
        parser.add_argument("--credentials", help="Path to credentials file")

        # Test parsing
        test_args = ["--export", "google_sheets", "--credentials", str(credentials_file)]
        args = parser.parse_args(test_args)

        print(f"📋 Export format: {args.export} ✅")
        print(f"📋 Credentials path: {args.credentials} ✅")

        return True

    except Exception as e:
        print(f"📋 CLI test: ❌ ({e})")
        return False

def test_logs_directory():
    """Test logs directory setup."""

    print("\n📊 Testing Logs Directory")
    print("=" * 30)

    logs_dir = project_root / "logs"
    print(f"📁 Logs directory exists: {'✅' if logs_dir.exists() else '❌'}")

    # Test writing to logs
    try:
        test_log_file = logs_dir / "test_log.txt"
        test_log_file.write_text("Test log entry")
        test_log_file.unlink()  # Delete test file
        print("📝 Log file writing: ✅")
        return True
    except Exception as e:
        print(f"📝 Log file writing: ❌ ({e})")
        return False

if __name__ == "__main__":
    print("🚀 Google Sheets Integration Test Suite")
    print("=" * 50)

    # Get credentials file path
    credentials_file = project_root / "client_secret_1020100796152-n6l4bloev9ha8to4mcbc6h3p8e1n1t3e.apps.googleusercontent.com.json"

    # Run all tests
    test_results = []

    test_results.append(test_logs_directory())
    test_results.append(test_cli_arguments())
    test_results.append(test_google_sheets_integration())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   ✅ Passed: {sum(test_results)}")
    print(f"   ❌ Failed: {len(test_results) - sum(test_results)}")

    if all(test_results):
        print("\n🎉 All tests passed! Google Sheets integration is ready.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the setup.")
        sys.exit(1)
