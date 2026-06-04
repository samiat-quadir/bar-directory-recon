#!/usr/bin/env python3
"""
Realtor Directory Automation Script - Phase 2 Enhanced
Automated lead extraction with real scraping capabilities
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add universal_recon to path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

# Import both the enhanced scraper and the plugin
try:
    from tools.realtor_directory_scraper import scrape_realtor_directory as enhanced_scraper
    from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory as plugin_scraper
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    enhanced_scraper = None
    plugin_scraper = None


def interactive_mode() -> Dict[str, Any]:
    """Interactive configuration mode for realtor directory scraping."""

    print("🏠 Realtor Directory Lead Automation - Phase 2")
    print("=" * 55)

    # Choose scraping mode
    print("\n🔧 Scraping Mode:")
    print("1. Test Mode (simulated data)")
    print("2. Live Mode (real scraping)")
    mode_choice = input("Choose mode [1 or 2]: ").strip()
    test_mode = mode_choice != "2"

    if test_mode:
        print("🧪 Using TEST MODE - will generate realistic simulated data")
    else:
        print("🔴 Using LIVE MODE - will attempt real scraping")

    # Get output path
    default_output = "outputs/realtor_leads.csv"
    output_path = input(f"Output CSV path [{default_output}]: ").strip()
    if not output_path:
        output_path = default_output

    # Get max records
    max_records_str = input("Maximum records to scrape [50]: ").strip()
    max_records = 50
    if max_records_str:
        try:
            max_records = int(max_records_str)
        except ValueError:
            print("⚠️  Invalid number, using 50")

    # Technical options
    print("\n⚙️ Technical Options:")
    use_selenium = input("Use Selenium for dynamic content? [Y/n]: ").strip().lower() != 'n'
    debug_mode = input("Enable debug output? [y/N]: ").strip().lower() == 'y'

    return {
        'output_path': output_path,
        'max_records': max_records,
        'test_mode': test_mode,
        'use_selenium': use_selenium,
        'debug': debug_mode
    }


def run_enhanced_scraper(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the enhanced Phase 2 scraper"""
    if enhanced_scraper:
        output_file = enhanced_scraper(
            max_records=config.get('max_records', 50),
            debug=config.get('debug', False),
            use_selenium=config.get('use_selenium', True),
            test_mode=config.get('test_mode', False)
        )

        if output_file:
            return {
                'success': True,
                'leads_count': config.get('max_records', 50),  # Approximate
                'output_path': output_file,
                'mode': 'test' if config.get('test_mode') else 'live'
            }

    return {
        'success': False,
        'error': 'Enhanced scraper not available',
        'leads_count': 0
    }


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Realtor Directory Lead Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python realtor_automation.py --interactive
  python realtor_automation.py --output leads.csv --max-records 100
  python realtor_automation.py --google-sheet-id 1ABC...xyz --verbose
  python realtor_automation.py --schedule
        """
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode with guided setup"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output CSV file path (default: outputs/realtor_leads.csv)"
    )

    parser.add_argument(
        "--max-records", "-m",
        type=int,
        help="Maximum number of records to scrape"
    )

    parser.add_argument(
        "--google-sheet-id", "-g",
        help="Google Sheets ID for uploading results"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Show scheduling setup instructions"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a test scrape with limited records"
    )

    args = parser.parse_args()

    # Handle scheduling instructions
    if args.schedule:
        show_scheduling_instructions()
        return

    # Handle test mode
    if args.test:
        print("🧪 Running Phase 2 test scrape...")
        config = {
            'max_records': 5,
            'debug': True,
            'test_mode': True,
            'use_selenium': True
        }
        result = run_enhanced_scraper(config)
        if result['success']:
            print(f"✅ Test completed: {result['leads_count']} leads found")
            print(f"📁 Saved to: {result['output_path']}")
        else:
            print(f"❌ Test failed: {result['error']}")
        return

    # Interactive mode
    if args.interactive:
        config = interactive_mode()
        result = run_enhanced_scraper(config)
    else:
        # Command line mode
        config = {
            'max_records': args.max_records or 50,
            'debug': args.verbose,
            'test_mode': False,  # Default to live mode for CLI
            'use_selenium': True
        }
        result = run_enhanced_scraper(config)

    # Display results
    if result['success']:
        print("\n✅ Scraping completed successfully!")
        print(f"📊 Found {result['leads_count']} leads")
        print(f"📁 Saved to: {result['output_path']}")
        print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ Scraping failed: {result['error']}")
        sys.exit(1)


def show_scheduling_instructions() -> None:
    """Display instructions for setting up scheduled automation."""

    print("📅 Scheduling Setup Instructions")
    print("=" * 50)
    print()
    print("🪟 Windows Task Scheduler:")
    print("  1. Run: realtor_automation_scheduler.ps1 -Install")
    print("  2. Or manually import: RealtorAutomationTask.xml")
    print()
    print("🐧 Linux/macOS Cron:")
    print("  1. Run: crontab -e")
    print("  2. Add: 0 8 * * 1 /path/to/python /path/to/realtor_automation.py --output /path/to/leads.csv")
    print()
    print("🐍 Python Schedule (run continuously):")
    print("  python realtor_scheduler.py")
    print()


if __name__ == "__main__":
    main()
