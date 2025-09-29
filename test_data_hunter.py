#!/usr/bin/env python3
"""
Data Hunter Test Script
Simple test and demonstration of the automated discovery system
"""

import sys

# Add src to path
sys.path.append("src")

from data_hunter import DataHunter


def test_discovery():
    """Test the discovery system."""
    print("=" * 60)
    print("DATA HUNTER TEST & DEMONSTRATION")
    print("=" * 60)

    # Initialize Data Hunter
    hunter = DataHunter()

    print(f"📁 Input directory: {hunter.input_dir}")
    print(f"📄 Config file: {hunter.config_path}")
    print(f"📋 Log directory: {hunter.logs_dir}")

    # Show configuration
    print("\n🔧 CURRENT CONFIGURATION:")
    print(f"Sources configured: {len(hunter.config['sources'])}")

    for source in hunter.config["sources"]:
        status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
        print(f"  • {source['name']}: {status}")
        print(f"    URL: {source['url']}")
        print(f"    Patterns: {len(source['patterns'])} defined")

    # Show notification settings
    notifications = hunter.config["notifications"]
    print("\n📧 NOTIFICATIONS:")
    print(f"  • Console: {'✅' if notifications['console']['enabled'] else '❌'}")
    print(f"  • Email: {'✅' if notifications['email']['enabled'] else '❌'}")
    print(f"  • Slack: {'✅' if notifications['slack']['enabled'] else '❌'}")

    # Show download settings
    download = hunter.config["download_settings"]
    print("\n⬇️ DOWNLOAD SETTINGS:")
    print(f"  • Max file size: {download['max_file_size_mb']}MB")
    print(f"  • Timeout: {download['timeout_seconds']}s")
    print(f"  • Retry attempts: {download['retry_attempts']}")

    print("\n🚀 RUNNING DISCOVERY TEST...")

    try:
        # Run discovery
        new_files = hunter.run_discovery()

        print("\n✅ Discovery completed successfully!")
        print(f"📄 New files found: {len(new_files)}")

        if new_files:
            print("\nNew files downloaded:")
            for file in new_files:
                print(f"  📄 {file}")
        else:
            print(
                "   (No new files found - this is normal if sources haven't been updated)"
            )

        # Show files in input directory
        input_files = list(hunter.input_dir.glob("*"))
        print(f"\n📁 Total files in input directory: {len(input_files)}")

        if input_files:
            print("Current files:")
            for file in input_files[-5:]:  # Show last 5 files
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  📄 {file.name} ({size_mb:.1f}MB)")

            if len(input_files) > 5:
                print(f"  ... and {len(input_files) - 5} more files")

    except Exception as e:
        print(f"❌ Discovery failed: {str(e)}")
        return False

    return True


def show_usage():
    """Show usage instructions."""
    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)

    print("\n🔧 CONFIGURATION:")
    print("1. Edit config/data_hunter_config.json to:")
    print("   • Enable/disable sources")
    print("   • Add new municipal websites")
    print("   • Configure notifications (email/Slack)")
    print("   • Adjust download settings")

    print("\n📧 EMAIL NOTIFICATIONS:")
    print("To enable email notifications, update config:")
    print("   • Set notifications.email.enabled: true")
    print("   • Add SMTP credentials")
    print("   • Add recipient email addresses")

    print("\n💬 SLACK NOTIFICATIONS:")
    print("To enable Slack notifications:")
    print("   • Create a Slack webhook URL")
    print("   • Set notifications.slack.enabled: true")
    print("   • Add webhook URL to config")

    print("\n🕒 SCHEDULING:")
    print("For automated daily runs:")
    print("   python src/data_hunter.py --schedule")
    print("   (Runs daily at configured time)")

    print("\n🚀 MANUAL RUNS:")
    print("For one-time discovery:")
    print("   python src/data_hunter.py --run-once")

    print("\n📄 PROCESSING NEW FILES:")
    print("After files are downloaded:")
    print("   python unified_scraper.py --pdf input/filename.pdf")
    print("   python final_hallandale_pipeline.py  # (adapt for other cities)")

    print("\n🔍 ADDING NEW SOURCES:")
    print("To add new municipal websites:")
    print("1. Edit config/data_hunter_config.json")
    print("2. Add new source object with:")
    print("   • name: City/County name")
    print("   • url: Website URL to scan")
    print("   • patterns: Regex patterns for file matching")
    print("   • enabled: true")


def main():
    """Main function."""
    if not test_discovery():
        return 1

    show_usage()

    print("\n" + "=" * 60)
    print("✅ DATA HUNTER TEST COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review downloaded files in input/ directory")
    print("2. Configure notifications if desired")
    print("3. Run: python src/data_hunter.py --schedule for automation")
    print("4. Process new files with existing pipeline scripts")

    return 0


if __name__ == "__main__":
    exit(main())
