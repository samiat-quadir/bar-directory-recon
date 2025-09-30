#!/usr/bin/env python3
"""
List Discovery Agent Demo - Phase 4
===================================

Demonstrates the capabilities of the List Discovery Agent including:
- Configuration setup
- URL monitoring
- File discovery and download
- Integration with Universal Project Runner
- Notification systems
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

try:
    from automation.universal_runner import UniversalRunner
    from list_discovery.agent import ListDiscoveryAgent

    LIST_DISCOVERY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print(
        "💡 Please install dependencies: pip install aiohttp aiofiles beautifulsoup4 PyYAML"
    )
    LIST_DISCOVERY_AVAILABLE = False


class ListDiscoveryDemo:
    """Demo class for the List Discovery Agent."""

    demo_config: Dict[str, Any]

    def __init__(self) -> None:
        self.demo_config = {
            "monitored_urls": [
                {"url": "https://httpbin.org/json", "name": "Demo API Endpoint"}
            ],
            "download_dir": "input/demo_discovered",
            "file_extensions": [".pdf", ".csv", ".json", ".txt"],
            "check_interval": 300,  # 5 minutes for demo
            "notifications": {"discord_webhook": None, "email": {"enabled": False}},
        }

    def show_banner(self) -> None:
        """Show demo banner."""
        print("\n" + "=" * 70)
        print("🔍 LIST DISCOVERY AGENT DEMO - PHASE 4")
        print("=" * 70)
        print("Bar Directory Reconnaissance - Web Monitoring Capabilities")
        print("-" * 70)
        print()

    def demo_configuration(self) -> None:
        """Demonstrate configuration management."""
        print("📋 CONFIGURATION DEMO")
        print("-" * 30)

        if not LIST_DISCOVERY_AVAILABLE:
            print("❌ List Discovery Agent not available")
            return

        # Create demo agent
        agent = ListDiscoveryAgent()

        # Show current config
        print("Current configuration:")
        print(f"  Monitored URLs: {len(agent.config.get('monitored_urls', []))}")
        print(f"  Download directory: {agent.config.get('download_dir', 'Not set')}")
        print(f"  File extensions: {agent.config.get('file_extensions', [])}")
        print(f"  Check interval: {agent.config.get('check_interval', 0)} seconds")

        # Add demo URL
        print("\n➕ Adding demo URL...")
        success = agent.add_url("https://example.com/licenses", "Demo County Licenses")

        if success:
            print("✅ Demo URL added successfully")
        else:
            print("⚠️ URL may already exist")

        # Show updated stats
        stats = agent.monitor.get_statistics()
        print("\nUpdated stats:")
        print(f"  Total monitored URLs: {stats['monitored_urls']}")
        print(f"  Files discovered: {stats['total_files_discovered']}")
        print(f"  Total downloads: {stats['total_downloads']}")

        print("✅ Configuration demo complete\n")

    async def demo_monitoring(self) -> None:
        """Demonstrate web monitoring capabilities."""
        print("🌐 WEB MONITORING DEMO")
        print("-" * 30)

        if not LIST_DISCOVERY_AVAILABLE:
            print("❌ List Discovery Agent not available")
            return

        # Create demo agent
        agent = ListDiscoveryAgent()

        print("Setting up demo monitoring...")

        # Configure with demo URLs that we can control
        demo_urls = [{"url": "https://httpbin.org/html", "name": "Demo HTML Page"}]

        agent.config["monitored_urls"] = demo_urls

        print(f"📡 Monitoring {len(demo_urls)} demo URL(s)...")

        # Run a single check
        try:
            downloaded_files = await agent.run_single_check()

            if downloaded_files:
                print(f"✅ Demo discovered {len(downloaded_files)} files:")
                for file_path in downloaded_files:
                    print(f"  📄 {file_path}")
            else:
                print("ℹ️ No files discovered (expected for demo URLs)")

        except Exception as e:
            print(f"⚠️ Demo monitoring error: {e}")
            print("💡 This is normal for demo URLs that don't contain files")

        print("✅ Monitoring demo complete\n")

    def demo_integration(self) -> None:
        """Demonstrate integration with Universal Project Runner."""

        print("🔗 INTEGRATION DEMO")
        print("-" * 30)

        if not LIST_DISCOVERY_AVAILABLE:
            print("❌ List Discovery Agent not available")
            return

        # Create Universal Runner instance
        runner = UniversalRunner()

        print("Universal Project Runner integration:")

        if runner.list_discovery:
            print("✅ List Discovery Agent initialized in Universal Runner")

            # Show integration capabilities
            print("\nIntegration features:")
            print("  🔄 Scheduled discovery runs")
            print("  📥 Automatic file processing")
            print("  📢 Unified notification system")
            print("  📊 Dashboard integration")
            print("  🗂️ Shared configuration management")

            # Show scheduler status
            try:
                config = runner.config
                discovery_config = config.get("schedules", {}).get("list_discovery", {})
                if discovery_config.get("enabled", True):
                    frequency = discovery_config.get("frequency", "hourly")
                    print(f"\n⏰ Discovery scheduled to run: {frequency}")
                else:
                    print("\n⚠️ Discovery scheduling disabled")
            except Exception as e:
                print(f"\n⚠️ Could not check scheduler config: {e}")
        else:
            print("❌ List Discovery Agent not available in Universal Runner")
            print("💡 Check dependencies and configuration")

        print("✅ Integration demo complete\n")

    def demo_file_processing(self) -> None:
        """Demonstrate file processing capabilities."""

        print("📁 FILE PROCESSING DEMO")
        print("-" * 30)

        # Create demo directory
        demo_dir = Path("input/demo_discovered")
        demo_dir.mkdir(parents=True, exist_ok=True)
        # Create demo files
        demo_files = [
            (
                "demo_licenses.csv",
                "name,address,license_type\nDemo Bar,123 Main St,Liquor",
            ),
            (
                "demo_permits.json",
                '{"permits": [{"name": "Demo Restaurant", "type": "Food"}]}',
            ),
            ("demo_list.txt", "Demo file for list discovery"),
        ]
        created_files = []
        for filename, content in demo_files:
            file_path = demo_dir / filename
            with open(file_path, "w") as f:
                f.write(content)
            created_files.append(file_path)
            print(f"📄 Created demo file: {file_path}")
        print(f"\n✅ Created {len(created_files)} demo files")
        if LIST_DISCOVERY_AVAILABLE:
            print("\nSimulating file processing...")
            for file_path in created_files:
                print(f"  🔄 Processing: {file_path.name}")
                # In real usage, this would trigger the pipeline
                # runner.process_input_file(file_path)
            print("✅ File processing simulation complete")
        else:
            print("⚠️ Cannot demonstrate processing - Universal Runner not available")
        print("✅ File processing demo complete\n")

    def demo_notifications(self) -> None:
        """Demonstrate notification capabilities."""
        print("📢 NOTIFICATION DEMO")
        print("-" * 30)

        if LIST_DISCOVERY_AVAILABLE:
            agent = ListDiscoveryAgent()

            if agent.monitor.notifier:
                print("Notification system available:")

                # Show configured channels
                config = agent.config.get("notifications", {})
                discord = config.get("discord_webhook")
                email = config.get("email", {})

                print(
                    f"  Discord: {'✅ Configured' if discord else '❌ Not configured'}"
                )
                print(
                    f"  Email: {'✅ Configured' if email.get('enabled') else '❌ Not configured'}"
                )

                # Demo notification content
                print("\nExample discovery notification:")
                print("  Title: 'New Lists Discovered: County Licenses'")
                print("  Content:")
                print("    • licenses_2024.pdf")
                print("    • permits_january.csv")
                print("    • business_list.xlsx")
                print("    Files are ready for processing...")

                print("\n💡 Configure webhooks/email in list_discovery/config.yaml")
            else:
                print("❌ Notification system not available")
        else:
            print("❌ Cannot demonstrate notifications - Agent not available")

        print("✅ Notification demo complete\n")

    def show_usage_examples(self) -> None:
        """Show usage examples."""

        print("💡 USAGE EXAMPLES")
        print("-" * 30)

        examples = [
            ("Setup List Discovery", "python list_discovery/agent.py setup"),
            (
                "Add monitoring URL",
                'python list_discovery/agent.py add "https://county.gov/licenses"',
            ),
            ("Run single check", "python list_discovery/agent.py check"),
            ("Start monitoring", "python list_discovery/agent.py monitor"),
            ("Show status", "python list_discovery/agent.py status"),
            ("Quick interface", "RunListDiscovery.bat"),
            ("Universal Runner", "RunAutomation.bat discovery"),
        ]

        for description, command in examples:
            print(f"  {description}:")
            print(f"    {command}")
            print()

        print("✅ Usage examples complete\n")

    def show_summary(self) -> None:
        """Show demo summary."""
        print("📋 DEMO SUMMARY")
        print("-" * 30)

        print("List Discovery Agent Phase 4 Features:")
        print("  ✅ Web page monitoring with change detection")
        print("  ✅ Automatic file download (PDF, CSV, Excel)")
        print("  ✅ Integration with Universal Project Runner")
        print("  ✅ Discord and Email notifications")
        print("  ✅ CLI interface and batch scripts")
        print("  ✅ Configurable monitoring schedules")
        print("  ✅ State persistence and statistics")
        print("  ✅ Error handling and logging")

        print("\nNext Steps:")
        print(
            "  1. Install dependencies: pip install -r list_discovery/requirements.txt"
        )
        print("  2. Setup configuration: python list_discovery/agent.py setup")
        print("  3. Add monitoring URLs: RunListDiscovery.bat add")
        print("  4. Start discovery: RunListDiscovery.bat check")
        print("  5. Enable scheduling: RunAutomation.bat schedule")

        print("\n🎉 List Discovery Agent ready for production use!")
        print("=" * 70)


async def main() -> None:
    """Run the complete demo."""
    demo = ListDiscoveryDemo()
    # Show banner
    demo.show_banner()
    print("🚀 Starting List Discovery Agent Demo...")
    print("This demo showcases Phase 4 capabilities without requiring live URLs\n")
    # Run demo sections
    demo.demo_configuration()
    await demo.demo_monitoring()
    demo.demo_integration()
    demo.demo_file_processing()
    demo.demo_notifications()
    demo.show_usage_examples()
    demo.show_summary()
    print("\n✅ Demo completed successfully!")
    print("💡 Check the generated files and logs for more details")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("💡 Check dependencies and try again")
