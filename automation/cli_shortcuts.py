"""
CLI Shortcuts and Hotkeys for Universal Project Runner
=====================================================

Provides convenient shortcuts for common pipeline operations.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.universal_runner import UniversalRunner


def quick_run(site: str) -> None:
    """Quick pipeline run for a single site."""
    print(f"🚀 Quick running pipeline for: {site}")
    runner = UniversalRunner()
    runner.run_pipeline_for_site(site)


def full_pipeline(sites: Optional[List[str]] = None) -> None:
    """Run full pipeline for all configured sites."""
    print("🔄 Running full pipeline...")
    runner = UniversalRunner()
    config_sites = runner.config["pipeline"]["sites"]
    target_sites = sites if sites else config_sites
    if not target_sites:
        print("❌ No sites configured. Please add sites to automation/config.yaml")
        return
    for site in target_sites:
        print(f"Processing {site}...")
        runner.run_pipeline_for_site(site)


def monitor_input() -> None:
    """Start input directory monitoring"""
    print("👀 Starting input directory monitoring...")
    print("Press Ctrl+C to stop")
    runner = UniversalRunner()
    runner.start_input_monitoring()


async def start_scheduler() -> None:
    """Start the automation scheduler"""
    print("⏰ Starting automation scheduler...")
    print("Press Ctrl+C to stop")
    runner = UniversalRunner()
    await runner.start_scheduler()


def show_status() -> None:
    """Show current system status"""
    runner = UniversalRunner()
    runner.show_status()


def generate_dashboard() -> None:
    """Generate status dashboard"""
    print("📊 Generating dashboard...")
    runner = UniversalRunner()
    runner.dashboard.generate_dashboard()
    print("✅ Dashboard generated successfully")


def test_notifications() -> None:
    """Test notification systems."""
    print("📢 Testing notification systems...")
    runner = UniversalRunner()
    # Test Discord notification if configured
    discord_webhook = runner.config["notifications"]["discord_webhook"]
    if discord_webhook:
        runner.notifier.send_info_notification(
            "Test Notification", "This is a test notification from the Universal Project Runner!"
        )
        print("✅ Discord notification sent")
    else:
        print("⚠️ Discord webhook not configured")
    # Test email notification if configured
    email_config = runner.config["notifications"]["email"]
    if email_config.get("enabled"):
        runner.notifier.send_info_notification("Test Email", "This is a test email from the Universal Project Runner!")
        print("✅ Email notification sent")
    else:
        print("⚠️ Email notifications not enabled")


def validate_system() -> None:
    """Validate system health and configuration"""
    print("🔍 Running system validation...")
    runner = UniversalRunner()

    # 1. Validate environment for pipeline execution
    print("\n--- Validating Pipeline Environment ---")
    executor = runner.pipeline
    if executor.validate_environment():
        print("✅ Pipeline environment validation passed.")
    else:
        print("❌ Pipeline environment validation failed. Check logs for details.")

    # 2. Check automation configuration
    print("\n--- Checking Automation Configuration ---")
    if runner.config:
        print("✅ Automation config loaded.")
        sites = runner.config.get("pipeline", {}).get("sites", [])
        if sites:
            print(f"   - Found {len(sites)} sites.")
        else:
            print("   - ⚠️ No sites configured in automation/config.yaml.")
    else:
        print("❌ Failed to load automation config.")

    # 3. Check List Discovery Agent
    print("\n--- Checking List Discovery Agent ---")
    if runner.list_discovery:
        print("✅ List Discovery Agent is available.")
        discovery_config = runner.list_discovery.config
        urls = discovery_config.get("monitored_urls", [])
        if urls:
            print(f"   - Found {len(urls)} URLs to monitor.")
        else:
            print("   - ⚠️ No URLs configured in list_discovery/config.yaml.")
    else:
        print("❌ List Discovery Agent not available. Run 'pip install -r list_discovery/requirements.txt'")

    print("\n✅ Validation complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Runner CLI Shortcuts")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quick run command
    quick_parser = subparsers.add_parser("quick", help="Quick pipeline run for a site")
    quick_parser.add_argument("site", help="Site to process")

    # Full pipeline command
    full_parser = subparsers.add_parser("full", help="Run full pipeline")
    full_parser.add_argument("--sites", nargs="*", help="Specific sites to process")
