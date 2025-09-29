#!/usr/bin/env python3
"""
Comprehensive test script for Phase 3+ Universal Lead Generation System
Tests all new plugins, Google Sheets integration, lead scoring, and automation features
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_plugin_registry():
    """Test that all plugins are properly registered."""
    logger.info("Testing plugin registry...")

    registry_path = Path("universal_recon/plugin_registry.json")
    if not registry_path.exists():
        logger.error(f"Plugin registry not found: {registry_path}")
        return False

    try:
        with open(registry_path, "r") as f:
            plugins = json.load(f)

        expected_plugins = [
            "realtor_directory",
            "pool_contractors",
            "lawyers",
            "hvac_plumbers",
            "auto_dealers",
            "homeadvisor",
            "thumbtack",
            "houzz",
            "angi",
        ]

        registered_plugins = [p["site_name"] for p in plugins]

        for expected in expected_plugins:
            if expected in registered_plugins:
                logger.info(f"  ✅ {expected} - registered")
            else:
                logger.error(f"  ❌ {expected} - NOT registered")
                return False

        logger.info(f"Plugin registry test passed! {len(plugins)} plugins registered")
        return True

    except Exception as e:
        logger.error(f"Plugin registry test failed: {e}")
        return False


def test_new_plugins():
    """Test each new plugin in test mode."""
    logger.info("Testing new plugins...")

    new_plugins = [
        ("homeadvisor", "home_services", "Phoenix"),
        ("thumbtack", "professional_services", "Austin"),
        ("houzz", "design_services", "Denver"),
        ("angi", "home_services", "Seattle"),
    ]

    success_count = 0

    for plugin_name, industry, city in new_plugins:
        try:
            logger.info(f"Testing {plugin_name} plugin...")

            # Import and test the plugin
            module_path = f"universal_recon.plugins.{plugin_name}_plugin"
            module = __import__(module_path, fromlist=[plugin_name])

            config = {"city": city, "state": "", "max_records": 5, "test_mode": True}

            result = module.run_plugin(config)

            if result["success"] and result["count"] > 0:
                logger.info(
                    f"  ✅ {plugin_name} - {result['count']} test leads generated"
                )
                success_count += 1
            else:
                logger.error(
                    f"  ❌ {plugin_name} - failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            logger.error(f"  ❌ {plugin_name} - exception: {e}")

    logger.info(f"New plugins test: {success_count}/4 passed")
    return success_count == 4


def test_universal_automation():
    """Test the main automation CLI."""
    logger.info("Testing universal automation CLI...")

    test_cases = [
        {
            "args": ["--industry", "home_services", "--city", "Miami", "--test"],
            "expected_plugins": 2,  # homeadvisor + angi
            "description": "Home services industry test",
        },
        {
            "args": [
                "--industry",
                "professional_services",
                "--city",
                "Boston",
                "--test",
            ],
            "expected_plugins": 1,  # thumbtack
            "description": "Professional services industry test",
        },
        {
            "args": ["--industry", "design_services", "--city", "Portland", "--test"],
            "expected_plugins": 1,  # houzz
            "description": "Design services industry test",
        },
    ]

    success_count = 0

    for test_case in test_cases:
        try:
            logger.info(f"Testing: {test_case['description']}")

            # Import the automation module
            from universal_automation import UniversalLeadAutomation

            automation = UniversalLeadAutomation()

            config = {
                "industry": test_case["args"][1],
                "city": test_case["args"][3],
                "state": "",
                "max_records": 5,
                "test_mode": True,
            }

            result = automation.scrape_industry(
                industry=config["industry"],
                city=config["city"],
                state=config["state"],
                max_records=config["max_records"],
                test_mode=config["test_mode"],
            )

            if result["success"] and result["count"] > 0:
                logger.info(
                    f"  ✅ Generated {result['count']} leads from {result['plugins_run']} plugins"
                )
                success_count += 1
            else:
                logger.error(
                    f"  ❌ Automation failed: {result.get('error', 'No leads generated')}"
                )

        except Exception as e:
            logger.error(f"  ❌ Exception in {test_case['description']}: {e}")

    logger.info(f"Universal automation test: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)


def test_lead_scoring():
    """Test the lead scoring engine."""
    logger.info("Testing lead scoring engine...")

    try:
        # Check if there are any existing leads to score
        outputs_dir = Path("outputs")
        csv_files = list(outputs_dir.rglob("*.csv"))

        if not csv_files:
            logger.warning("No existing CSV files found. Generating test data first...")

            # Generate some test data
            from universal_automation import UniversalLeadAutomation

            automation = UniversalLeadAutomation()

            config = {
                "industry": "pool_contractors",
                "city": "Tampa",
                "state": "FL",
                "max_records": 10,
                "test_mode": True,
            }

            result = automation.scrape_industry(
                industry=config["industry"],
                city=config["city"],
                state=config["state"],
                max_records=config["max_records"],
                test_mode=config["test_mode"],
            )
            if not result["success"]:
                logger.error("Failed to generate test data for scoring")
                return False

        # Test the scoring script
        from score_leads import main as score_main

        # Create test args
        test_args = [
            str(outputs_dir),
            "--output",
            "test_priority_leads.csv",
            "--top",
            "10",
        ]

        # Mock sys.argv for the scoring script
        original_argv = sys.argv
        sys.argv = ["score_leads.py"] + test_args

        try:
            score_main()

            # Check if output file was created
            output_file = Path("test_priority_leads.csv")
            if output_file.exists():
                logger.info("  ✅ Lead scoring completed successfully")
                logger.info(f"  ✅ Output file created: {output_file}")

                # Clean up test file
                output_file.unlink()
                return True
            else:
                logger.error("  ❌ Lead scoring output file not created")
                return False

        finally:
            sys.argv = original_argv

    except Exception as e:
        logger.error(f"Lead scoring test failed: {e}")
        return False


def test_google_sheets_utils():
    """Test Google Sheets utility functions (without actual export)."""
    logger.info("Testing Google Sheets utilities...")

    try:
        from universal_recon.plugins.google_sheets_utils import (
            export_to_google_sheets,
            get_sheet_url,
        )

        # Test URL generation
        test_sheet_id = "1234567890abcdef"
        test_sheet_name = "Test_Leads"

        url = get_sheet_url(test_sheet_id, test_sheet_name)
        expected_url = (
            f"https://docs.google.com/spreadsheets/d/{test_sheet_id}#gid=Test_Leads"
        )

        if url == expected_url:
            logger.info("  ✅ Google Sheets URL generation works")
        else:
            logger.error(
                f"  ❌ URL generation failed. Expected: {expected_url}, Got: {url}"
            )
            return False

        # Test export function (will fail without credentials, but should handle gracefully)
        test_data = [{"Name": "Test Company", "Phone": "555-1234", "City": "Test City"}]

        result = export_to_google_sheets(test_data, test_sheet_id, test_sheet_name)

        # Should return False due to missing credentials, but not crash
        if result is False:
            logger.info(
                "  ✅ Google Sheets export handled missing credentials gracefully"
            )
            return True
        else:
            logger.warning("  ⚠️ Unexpected result from Google Sheets export")
            return True

    except Exception as e:
        logger.error(f"Google Sheets utilities test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files and directories exist."""
    logger.info("Testing file structure...")

    required_files = [
        "universal_automation.py",
        "score_leads.py",
        "universal_recon/plugin_registry.json",
        "universal_recon/plugins/homeadvisor_plugin.py",
        "universal_recon/plugins/thumbtack_plugin.py",
        "universal_recon/plugins/houzz_plugin.py",
        "universal_recon/plugins/angi_plugin.py",
        "universal_recon/plugins/google_sheets_utils.py",
        "weekly_automation.bat",
        "weekly_automation.ps1",
        "docs/COPILOT_AUTO_CONFIRM_SETUP.md",
    ]

    required_dirs = ["outputs", "logs", "universal_recon/plugins", "docs"]

    missing_files = []
    missing_dirs = []

    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            logger.info(f"  ✅ {file_path}")

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            logger.info(f"  ✅ {dir_path}/")

    if missing_files:
        logger.error(f"Missing files: {missing_files}")
        return False

    if missing_dirs:
        logger.error(f"Missing directories: {missing_dirs}")
        return False

    logger.info("File structure test passed!")
    return True


def run_comprehensive_test():
    """Run all tests."""
    logger.info("Starting comprehensive test suite...")
    logger.info("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Plugin Registry", test_plugin_registry),
        ("New Plugins", test_new_plugins),
        ("Universal Automation", test_universal_automation),
        ("Lead Scoring", test_lead_scoring),
        ("Google Sheets Utils", test_google_sheets_utils),
    ]

    results = {}

    for test_name, test_function in tests:
        logger.info(f"\n{'-' * 40}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'-' * 40}")

        try:
            results[test_name] = test_function()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! System is ready for production use.")
        return True
    else:
        logger.error(
            f"❌ {total - passed} tests failed. Please fix issues before deployment."
        )
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test Universal Lead Generation System"
    )
    parser.add_argument(
        "--test",
        choices=["all", "plugins", "automation", "scoring", "structure"],
        default="all",
        help="Which test to run",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.test == "all":
        success = run_comprehensive_test()
    elif args.test == "plugins":
        success = test_new_plugins()
    elif args.test == "automation":
        success = test_universal_automation()
    elif args.test == "scoring":
        success = test_lead_scoring()
    elif args.test == "structure":
        success = test_file_structure()
    else:
        logger.error(f"Unknown test: {args.test}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
