#!/usr/bin/env python3
"""
Command Line Interface for the Unified Scraping Framework
Provides easy access to scraping functionality via command line.
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader
from src.orchestrator import ScrapingOrchestrator, create_config, quick_scrape


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Directory Scraping Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick scrape with minimal setup
  python unified_scraper.py quick --name "lawyers" --url "https://example.com" --selector ".lawyer-card"

  # Create configuration template
  python unified_scraper.py config --name "realtor_directory" \\
      --url "https://realtors.com" --output "config/realtors.json"

  # Run scraping with configuration file
  python unified_scraper.py scrape --config "config/realtors.json"

  # List available configurations
  python unified_scraper.py list
        """,
    )

    # Global options
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress verbose output (errors only)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug output")
    parser.add_argument(
        "--config-dir",
        default="config",
        help="Configuration directory (default: config)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quick scrape command
    quick_parser = subparsers.add_parser("quick", help="Quick scrape with minimal configuration")
    quick_parser.add_argument("--name", required=True, help="Name for the scraping session")
    quick_parser.add_argument("--url", required=True, help="Base URL to scrape")
    quick_parser.add_argument(
        "--selector", default=".listing-item", help="CSS selector for listing items"
    )
    quick_parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to scrape")
    quick_parser.add_argument(
        "--headless", action="store_true", default=True, help="Run in headless mode"
    )
    quick_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Configuration command
    config_parser = subparsers.add_parser("config", help="Create configuration template")
    config_parser.add_argument("--name", required=True, help="Name for the configuration")
    config_parser.add_argument("--url", required=True, help="Base URL for scraping")
    config_parser.add_argument("--output", required=True, help="Output path for configuration file")
    config_parser.add_argument(
        "--industry", help="Industry type (lawyers, realtors, contractors, etc.)"
    )

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Run scraping with configuration file")
    scrape_parser.add_argument("--config", required=True, help="Path to configuration file")
    scrape_parser.add_argument(
        "--headless", action="store_true", default=True, help="Run in headless mode"
    )
    scrape_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    scrape_parser.add_argument("--max-records", type=int, help="Maximum records to extract")
    scrape_parser.add_argument("--max-pages", type=int, help="Maximum pages to process")

    # List command
    list_parser = subparsers.add_parser("list", help="List available configurations")
    list_parser.add_argument("--config-dir", default="config", help="Configuration directory")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate configuration file")
    validate_parser.add_argument("--config", required=True, help="Path to configuration file")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test scraping setup without extraction")
    test_parser.add_argument("--config", required=True, help="Path to configuration file")
    test_parser.add_argument("--pages", type=int, default=1, help="Number of pages to test")

    # Add notification test subcommand
    notify_parser = subparsers.add_parser("notify-test", help="Send test notification")
    notify_parser.add_argument("--config", required=True, help="Configuration file path")
    notify_parser.add_argument(
        "--type",
        choices=["email", "sms", "slack", "all"],
        default="all",
        help="Type of notification to test",
    )
    notify_parser.set_defaults(func=handle_notification_test)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "quick":
            handle_quick_scrape(args)
        elif args.command == "config":
            handle_create_config(args)
        elif args.command == "scrape":
            handle_scrape(args)
        elif args.command == "list":
            handle_list_configs(args)
        elif args.command == "validate":
            handle_validate_config(args)
        elif args.command == "test":
            handle_test_config(args)
        elif args.command == "notify-test":
            handle_notification_test(args)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def handle_quick_scrape(args: argparse.Namespace) -> None:
    """Handle quick scrape command."""
    print(f"🚀 Starting quick scrape: {args.name}")
    print(f"   URL: {args.url}")
    print(f"   Selector: {args.selector}")
    print(f"   Max Pages: {args.max_pages}")
    print()

    result = quick_scrape(
        name=args.name,
        base_url=args.url,
        list_selector=args.selector,
        max_pages=args.max_pages,
    )

    if result.get("success"):
        print("✅ Quick scrape completed successfully!")
        print(f"   Records extracted: {result.get('records_extracted', 0)}")
        print(f"   Runtime: {result.get('runtime_formatted', 'Unknown')}")

        output_files = result.get("output_files", [])
        if output_files:
            print("   Output files:")
            for file_path in output_files:
                print(f"     - {file_path}")
    else:
        print("❌ Quick scrape failed!")
        error = result.get("error", "Unknown error")
        print(f"   Error: {error}")


def handle_create_config(args: argparse.Namespace) -> None:
    """Handle create config command."""
    print(f"📝 Creating configuration: {args.name}")
    print(f"   URL: {args.url}")
    print(f"   Output: {args.output}")

    try:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create configuration
        config_path = create_config(args.name, args.url, args.output)

        print("✅ Configuration created successfully!")
        print(f"   File: {config_path}")
        print()
        print("💡 Next steps:")
        print("   1. Edit the configuration file to customize selectors")
        print("   2. Run: python unified_scraper.py validate --config " + args.output)
        print("   3. Run: python unified_scraper.py scrape --config " + args.output)

    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")


def handle_scrape(args: argparse.Namespace) -> None:
    """Handle scrape command."""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return

    print("🔍 Starting scraping session")
    print(f"   Config: {config_path}")
    print(f"   Headless: {args.headless}")
    print()

    try:
        # Modify config for CLI options
        if args.max_records or args.max_pages:
            print("📝 Applying CLI overrides...")
            # This would require loading and modifying the config
            # For now, just show the message

        orchestrator = ScrapingOrchestrator(config_path)
        result = orchestrator.run_scraping()

        if result.get("success"):
            print("✅ Scraping completed successfully!")
            print(f"   Records extracted: {result.get('records_extracted', 0)}")
            print(f"   URLs processed: {result.get('urls_processed', 0)}")
            print(f"   URLs failed: {result.get('urls_failed', 0)}")
            print(f"   Runtime: {result.get('runtime_formatted', 'Unknown')}")

            output_files = result.get("output_files", [])
            if output_files:
                print("   Output files:")
                for file_path in output_files:
                    print(f"     - {file_path}")

            # Show statistics if available
            stats = result.get("statistics", {})
            if stats:
                print(f"   Pages per minute: {stats.get('pages_per_minute', 0):.2f}")
                print(f"   Records per minute: {stats.get('records_per_minute', 0):.2f}")
        else:
            print("❌ Scraping failed!")

    except Exception as e:
        print(f"❌ Scraping error: {e}")


def handle_list_configs(args: argparse.Namespace) -> None:
    """Handle list configs command."""
    config_dir = Path(args.config_dir)

    if not config_dir.exists():
        print(f"❌ Configuration directory not found: {config_dir}")
        return

    try:
        loader = ConfigLoader(str(config_dir))
        configs = loader.list_configs()

        if configs:
            print(f"📋 Available configurations ({len(configs)}):")
            print()

            for config_name in configs:
                config_files = list(config_dir.glob(f"{config_name}.*"))
                if config_files:
                    config_file = config_files[0]
                    try:
                        config = loader.load_config(config_file)
                        print(f"   📄 {config_name}")
                        print(f"      Description: {config.description}")
                        print(f"      Base URL: {config.base_url}")
                        print(f"      File: {config_file}")
                        print()
                    except Exception as e:
                        print(f"   ❌ {config_name} (Error: {e})")
                        print()
        else:
            print("📋 No configurations found")
            print(f"   Directory: {config_dir}")
            print()
            print("💡 Create a configuration with:")
            print("   python unified_scraper.py config --name example \\")
            print("       --url https://example.com --output config/example.json")

    except Exception as e:
        print(f"❌ Error listing configurations: {e}")


def handle_validate_config(args: argparse.Namespace) -> None:
    """Handle validate config command."""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return

    print(f"🔍 Validating configuration: {config_path}")

    try:
        loader = ConfigLoader()
        config = loader.load_config(config_path)

        print("✅ Configuration is valid!")
        print(f"   Name: {config.name}")
        print(f"   Description: {config.description}")
        print(f"   Base URL: {config.base_url}")

        # Validate selectors
        selectors = config.data_extraction.get("selectors", {})
        if selectors:
            print(f"   Data selectors: {len(selectors)} configured")

            issues = loader.validate_selectors(selectors)
            if issues:
                print("   ⚠️  Selector issues found:")
                for issue in issues:
                    print(f"     - {issue}")
            else:
                print("   ✅ All selectors are properly configured")

        # Check pagination settings
        pagination = config.pagination
        if pagination.get("enabled"):
            print(f"   Pagination: Enabled (max {pagination.get('max_pages', 'unlimited')} pages)")
        else:
            print("   Pagination: Disabled")

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")


def handle_test_config(args: argparse.Namespace) -> None:
    """Handle test config command."""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return

    print(f"🧪 Testing configuration: {config_path}")
    print(f"   Test pages: {args.pages}")
    print()

    try:
        # For testing, we would create a modified orchestrator that only tests navigation
        # This is a simplified version
        print("🚀 Test mode not fully implemented yet")
        print("   This would test:")
        print("   - URL navigation")
        print("   - Element detection")
        print("   - Pagination discovery")
        print("   - Selector validation")

    except Exception as e:
        print(f"❌ Test failed: {e}")


def handle_notification_test(args: argparse.Namespace) -> None:
    """Handle notification test command."""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return

    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load_config(str(config_path))

        print(f"📧 Testing notifications for: {config.name}")

        # Create notification agent from config
        from src.notification_agent import NotificationAgent

        notification_config = getattr(config, "notifications", {})

        if not notification_config or not notification_config.get("enabled"):
            print("⚠️  Notifications are disabled in configuration")
            return

        agent = NotificationAgent(notification_config)

        notification_type = getattr(args, "type", "all")
        print(f"🔔 Sending test notification ({notification_type})...")

        success = agent.send_test_notification_by_type(notification_type)

        if success:
            print(f"✅ Test {notification_type} notification sent successfully!")
        else:
            print(
                f"❌ Failed to send test {notification_type} notification. Check configuration and logs."
            )

    except Exception as e:
        print(f"❌ Error testing notifications: {e}")


def print_banner() -> None:
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                 Unified Scraping Framework                  ║
    ║              Professional Directory Automation              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    print_banner()
    main()
