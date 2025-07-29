"""
Phase 3 & 4 Automation Demo Script
==================================

This script demonstrates the key capabilities of the Universal Project Runner
and the List Discovery Agent automation systems. It showcases all major
features in a guided demo.
"""

import time
import sys
from pathlib import Path
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import automation modules
try:
    from automation.universal_runner import UniversalRunner
    from automation.notifier import NotificationManager
    from automation.dashboard import DashboardManager
    from automation.pipeline_executor import PipelineExecutor
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import automation modules: {e}")
    print("Please run 'RunAutomation.bat install' and 'pip install -r list_discovery/requirements.txt' first")
    sys.exit(1)


def print_header(title: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def print_step(step: str) -> None:
    """Print a step description"""
    print(f"\n🔹 {step}")


def wait_for_user() -> None:
    """Wait for user to press Enter"""
    input("\nPress Enter to continue...")


def demo_configuration() -> None:
    """Demonstrate configuration loading"""
    print_header("CONFIGURATION MANAGEMENT DEMO")

    print_step("Loading automation configuration...")

    runner = UniversalRunner()
    config = runner.config

    print("✅ Configuration loaded successfully!")
    print(f"   • Configured sites: {len(config['pipeline']['sites'])}")
    print(f"   • Input directories: {len(config['monitoring']['input_directories'])}")
    print(f"   • File patterns: {len(config['monitoring']['file_patterns'])}")

    # Split long notification line for readability
    discord_status = '✅' if config['notifications']['discord_webhook'] else '❌'
    email_status = '✅' if config['notifications']['email']['enabled'] else '❌'
    print(f"   • Notification channels: Discord: {discord_status}, Email: {email_status}")

    # Show List Discovery config
    if runner.list_discovery:
        discovery_config = runner.list_discovery.config
        print(f"   • List Discovery URLs: {len(discovery_config.get('monitored_urls', []))}")

    wait_for_user()


def demo_dashboard() -> None:
    """Demonstrate dashboard generation"""
    print_header("STATUS DASHBOARD DEMO")

    print_step("Generating status dashboard...")

    # Create sample status data
    dashboard = DashboardManager({
        'local_html': {'enabled': True, 'output_path': 'output/demo_dashboard.html'},
        'google_sheets': {'enabled': False}
    })

    # Add some sample data
    dashboard.update_site_status("demo-site-1.com", "success", {"score": 85.2})
    dashboard.update_site_status("demo-site-2.com", "failed", {"error": "Connection timeout"})
    dashboard.update_site_status("demo-site-3.com", "success", {"score": 92.1})
    # dashboard.update_log_event("List Discovery", "Downloaded 3 new files from 'County Licenses'")
    # If you want to log an event, use the correct method if available, e.g.:
    # dashboard.add_log_event("List Discovery", "Downloaded 3 new files from 'County Licenses'")

    # Generate dashboard
    dashboard.generate_dashboard()

    dashboard_path = Path("output/demo_dashboard.html")
    if dashboard_path.exists():
        print("✅ Demo dashboard generated successfully!")
        print(f"   📄 Location: {dashboard_path}")
        print(f"   📊 File size: {dashboard_path.stat().st_size:,} bytes")

        # Show dashboard stats
        stats = dashboard.get_stats_summary()
        print(f"   📈 Total runs: {stats['total_runs']}")
        print(f"   ✅ Success rate: {stats['success_rate']:.1f}%")

        open_dashboard = input("\n🌐 Open dashboard in browser? (y/n): ")
        if open_dashboard.lower() == 'y':
            import webbrowser
            webbrowser.open(f"file://{dashboard_path.absolute()}")
    else:
        print("❌ Failed to generate dashboard")

    wait_for_user()


def demo_notifications() -> None:
    """Demonstrate notification system"""
    print_header("NOTIFICATION SYSTEM DEMO")

    print_step("Initializing notification manager...")

    # Create notification manager with demo config
    notifier = NotificationManager({
        'discord_webhook': None,  # Set to None for demo
        'email': {'enabled': False}  # Disabled for demo
    })

    print("✅ Notification manager initialized")
    print("   ℹ️ Demo mode: notifications will be logged but not sent")

    print_step("Testing different notification types...")

    # Demonstrate different notification types
    notifications = [
        ("success", "Pipeline Completed Successfully", "Processed 3 sites with 100% success rate"),
        ("warning", "Validation Issues Detected", "2 minor validation warnings found"),
        ("error", "Pipeline Execution Failed", "Site example.com failed due to timeout"),
        ("info", "Scheduled Task Started", "Daily scraping task initiated"),
        ("discovery", "New Lists Discovered: County Licenses",
         "Downloaded 3 new files: licenses.pdf, permits.csv, data.xlsx")
    ]

    for notif_type, title, message in notifications:
        print(f"   📧 Sending {notif_type} notification: {title}")
        if notif_type == "success":
            notifier.send_success_notification(title, message)
        elif notif_type == "warning":
            notifier.send_warning_notification(title, message)
        elif notif_type == "error":
            notifier.send_error_notification(title, message)
        elif notif_type == "info":
            notifier.send_info_notification(title, message)
        elif notif_type == "discovery":
            # Use a generic info notification for the demo
            notifier.send_info_notification(title, message)

        time.sleep(1)  # Brief pause between notifications

    print("\n✅ All notification types demonstrated!")
    print("   📝 Check logs/automation/universal_runner.log for notification details")

    wait_for_user()


def demo_input_monitoring() -> None:
    """Demonstrate input file monitoring"""
    print_header("INPUT MONITORING DEMO")

    print_step("Setting up input directory monitoring...")

    # Ensure input directory exists
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    # Create sample input files
    sample_files = [
        ("sites.json", {"sites": ["demo-bar-1.com", "demo-bar-2.com"]}),
        ("config.csv", "site,type,priority\ndemo-bar-3.com,restaurant,high\ndemo-bar-4.com,bar,medium"),
        ("snapshot.html", "<html><head><title>Demo Snapshot</title></head><body><h1>Demo Bar</h1></body></html>")
    ]

    print("✅ Input monitoring configured")
    print(f"   📁 Monitoring directory: {input_dir.absolute()}")
    print("   🔍 Watching for: *.json, *.csv, *.html files")

    print_step("Creating sample input files...")

    for filename, content in sample_files:
        file_path = input_dir / filename
        if isinstance(content, dict):
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)
        else:
            with open(file_path, 'w') as f:
                f.write(str(content))

        print(f"   📄 Created: {filename}")

    print("\n✅ Sample files created!")
    print("   ℹ️ In production, these files would trigger automatic processing")
    print("   🔄 File types supported: JSON site lists, CSV data, HTML snapshots")

    wait_for_user()


def demo_pipeline_validation() -> None:
    """Demonstrate pipeline validation"""
    print_header("PIPELINE VALIDATION DEMO")

    print_step("Validating pipeline environment...")

    executor = PipelineExecutor({
        'sites': ['demo-site.com'],
        'default_flags': ['--schema-matrix', '--emit-status'],
        'timeout': 300,
        'retry_count': 2
    })

    # Test environment validation
    print("🔍 Checking environment...")
    if executor.validate_environment():
        print("✅ Environment validation passed")
        print("   • Python interpreter: Available")
        print("   • Universal recon module: Importable")
        print("   • Required directories: Present")
    else:
        print("⚠️ Environment validation issues detected")
        print("   • Some components may not be properly configured")

    print_step("Testing pipeline configuration...")

    # Show available sites
    available_sites = executor.get_available_sites()
    print("✅ Pipeline configuration loaded")
    print(f"   📊 Configured sites: {len(available_sites)}")
    print(f"   ⏱️ Execution timeout: {executor.timeout} seconds")
    print(f"   🔄 Retry attempts: {executor.retry_count}")

    wait_for_user()


def demo_system_status() -> None:
    """Demonstrate system status reporting"""
    print_header("SYSTEM STATUS DEMO")

    print_step("Gathering system information...")

    runner = UniversalRunner()

    # Show basic system status
    print("✅ Universal Runner Status:")
    print("   🔧 Configuration: Loaded")
    print("   📊 Dashboard Manager: Ready")
    print("   📧 Notification Manager: Ready")
    print("   🔄 Pipeline Executor: Ready")
    if runner.list_discovery:
        print("   🌐 List Discovery Agent: Ready")

    # Show file system status
    important_paths = [
        ("Configuration", "automation/config.yaml"),
        ("Log directory", "logs/automation/"),
        ("Input directory", "input/"),
        ("Output directory", "output/"),
        ("Dashboard", "output/dashboard.html"),
        ("Discovery Config", "list_discovery/config.yaml")
    ]

    print("\n📁 File System Status:")
    for name, path in important_paths:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_file():
                size = path_obj.stat().st_size
                print(f"   ✅ {name}: {size:,} bytes")
            else:
                file_count = len(list(path_obj.glob("*")))
                print(f"   ✅ {name}: {file_count} files")
        else:
            print(f"   ❌ {name}: Not found")

    # Show recent activity (simulated)
    print("\n📋 Recent Activity (Simulated):")
    recent_activities = [
        "2025-07-12 10:30 - Dashboard generated successfully",
        "2025-07-12 10:00 - List Discovery found 2 new files from 'City Permits'",
        "2025-07-12 09:15 - Pipeline completed for demo-site.com",
        "2025-07-12 08:00 - Scheduled scraping task started",
        "2025-07-12 06:00 - Daily health check passed"
    ]

    for activity in recent_activities:
        print(f"   📝 {activity}")

    wait_for_user()


def demo_cli_integration() -> None:
    """Demonstrate CLI integration"""
    print_header("CLI INTEGRATION DEMO")

    print_step("Demonstrating command-line interfaces...")

    print("🖥️ Available Command Interfaces:")
    print("\n1. Windows Batch Script (RunAutomation.bat):")
    print("   • RunAutomation.bat quick example.com")
    print("   • RunAutomation.bat full")
    print("   • RunAutomation.bat dashboard")
    print("   • RunAutomation.bat monitor")
    print("   • RunAutomation.bat discovery")

    print("\n2. List Discovery CLI (RunListDiscovery.bat):")
    print("   • RunListDiscovery.bat check")
    print("   • RunListDiscovery.bat status")
    print("   • RunListDiscovery.bat add <url>")

    print("\n3. PowerShell Hotkeys (AutomationHotkeys.ps1):")
    print("   • ur-quick example.com")
    print("   • ur-full")
    print("   • ur-dashboard")
    print("   • ur-status")

    print("\n4. Python CLI (automation/cli_shortcuts.py):")
    print("   • python automation/cli_shortcuts.py quick example.com")
    print("   • python automation/cli_shortcuts.py full")
    print("   • python automation/cli_shortcuts.py dashboard")
    print("   • python automation/cli_shortcuts.py discovery")

    print("\n5. Direct Python API:")
    print("   • from automation.universal_runner import UniversalRunner")
    print("   • runner = UniversalRunner()")
    print("   • runner.run_pipeline_for_site('example.com')")

    print("\n✅ Multiple access methods provide flexibility for different use cases")
    print("   🔧 Batch scripts for Windows automation")
    print("   ⚡ PowerShell hotkeys for interactive use")
    print("   🐍 Python APIs for programmatic access")

    wait_for_user()


def main() -> None:
    """Main demo function"""
    print_header("PHASE 3 & 4 AUTOMATION - LIVE DEMO")

    print("""
🔍 Welcome to the Universal Project Runner & List Discovery Agent demonstration!

This demo will showcase the key capabilities of the automation systems:

1. Configuration Management
2. Status Dashboard Generation
3. Notification System
4. Input File Monitoring
5. Pipeline Validation
6. System Status Reporting
7. CLI Integration
8. List Discovery Agent

Each section demonstrates real functionality with sample data.
    """)

    input("Press Enter to start the demo...")

    try:
        if not AUTOMATION_AVAILABLE:
            return

        demo_configuration()
        demo_dashboard()
        demo_notifications()
        demo_input_monitoring()
        demo_pipeline_validation()
        demo_system_status()
        demo_cli_integration()

        # Add List Discovery Demo
        runner = UniversalRunner()
        if runner.list_discovery:
            print_header("LIST DISCOVERY AGENT DEMO")
            print_step("Demonstrating web monitoring for new files...")
            # A more complete demo would be in list_discovery/demo.py
            # This is a brief integration check
            stats = runner.list_discovery.monitor.get_statistics()
            print(f"   • Monitored URLs: {stats['monitored_urls']}")
            print(f"   • Total files discovered: {stats['total_files_discovered']}")
            print(f"   • Recent downloads (7 days): {stats['recent_downloads_7days']}")
            wait_for_user()

        print_header("DEMO COMPLETED SUCCESSFULLY")

        print("""
🎉 Congratulations! You've completed the Automation demo.

Key takeaways:
✅ Universal Project Runner provides comprehensive automation
✅ List Discovery Agent automatically finds new data sources
✅ Multi-channel notifications keep you informed
✅ Real-time dashboard shows system status
✅ Input monitoring enables hands-free operation
✅ Multiple CLI interfaces offer flexibility
✅ Robust error handling and validation

Next steps:
1. Configure automation/config.yaml and list_discovery/config.yaml
2. Set up Discord/Email notifications
3. Add your target sites and URLs to the configurations
4. Run 'RunAutomation.bat schedule' to start full automation

Thank you for exploring the Bar Directory Reconnaissance Automation Suite!
        """)

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        print("Please check the error and try again.")


if __name__ == "__main__":
    main()
