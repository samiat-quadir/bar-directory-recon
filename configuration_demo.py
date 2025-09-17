#!/usr/bin/env python3
"""
Enhanced Configuration Demo

This script demonstrates the new configuration system with validation,
environment variable support, and template generation.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from automation.enhanced_config_loader import ConfigLoader, generate_config_template
    from automation.enhanced_dashboard import EnhancedDashboardManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you've installed the required dependencies:")
    print("  pip install -r requirements-core.txt")
    sys.exit(1)


def demo_configuration_loading():
    """Demonstrate configuration loading with validation."""
    print("🔧 Configuration Loading Demo")
    print("=" * 50)

    try:
        # Create config loader
        loader = ConfigLoader()

        # Try to load automation config
        print("📝 Loading automation configuration...")
        config = loader.load_automation_config()

        print("✅ Configuration loaded successfully!")
        print(f"   - Schedules configured: {len(config.schedules.__dict__)}")
        print(f"   - Monitoring enabled: {config.monitoring.auto_process}")
        print(f"   - Dashboard enabled: {config.dashboard.local_html.enabled}")
        print(f"   - Pipeline sites: {len(config.pipeline.sites)}")

        return config

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return None


def demo_template_generation():
    """Demonstrate template generation."""
    print("\n📄 Template Generation Demo")
    print("=" * 50)

    try:
        # Generate automation config template
        template_path = generate_config_template(
            "automation", "automation/config.template.yaml"
        )
        print(f"✅ Generated automation template: {template_path}")

        # Generate list discovery template
        template_path = generate_config_template(
            "list_discovery", "list_discovery/config.template.yaml"
        )
        print(f"✅ Generated list discovery template: {template_path}")

    except Exception as e:
        print(f"❌ Template generation error: {e}")


def demo_dashboard_generation(config):
    """Demonstrate enhanced dashboard generation."""
    print("\n📊 Dashboard Generation Demo")
    print("=" * 50)

    if not config:
        print("❌ Skipping dashboard demo - no config available")
        return

    try:
        # Create dashboard manager
        dashboard = EnhancedDashboardManager(config.dashboard.model_dump())

        # Add some sample data
        dashboard.update_site_status("example-bar.com", "success", 2.5)
        dashboard.update_site_status(
            "another-bar.com", "failed", None, "Connection timeout"
        )
        dashboard.update_site_status("test-bar.com", "running")

        # Generate dashboard
        dashboard.generate_dashboard()

        output_path = Path(config.dashboard.local_html.output_path)
        if output_path.exists():
            print(f"✅ Dashboard generated: {output_path}")
            print(f"   File size: {output_path.stat().st_size:,} bytes")
            print(f"   Open in browser: file://{output_path.absolute()}")
        else:
            print("❌ Dashboard file not found")

    except Exception as e:
        print(f"❌ Dashboard generation error: {e}")


def demo_environment_variables():
    """Demonstrate environment variable support."""
    print("\n🌍 Environment Variables Demo")
    print("=" * 50)

    # Set some demo environment variables
    os.environ["AUTOMATION_DISCORD_WEBHOOK"] = "https://discord.com/api/webhooks/demo"
    os.environ["AUTOMATION_EMAIL_ENABLED"] = "true"
    os.environ["AUTOMATION_PIPELINE_TIMEOUT"] = "7200"

    try:
        # Create a temporary config with environment variables
        config_content = """
notifications:
  discord_webhook: "${AUTOMATION_DISCORD_WEBHOOK:}"
  email:
    enabled: ${AUTOMATION_EMAIL_ENABLED:false}

pipeline:
  timeout: ${AUTOMATION_PIPELINE_TIMEOUT:3600}
  sites:
    - "${AUTOMATION_SITE1:example.com}"
"""

        # Write temporary config
        temp_config = Path("temp_demo_config.yaml")
        temp_config.write_text(config_content)

        # Load config with environment substitution
        loader = ConfigLoader()
        config = loader.load_automation_config(str(temp_config))

        print("✅ Environment variable substitution working:")
        print(
            f"   - Discord webhook: {'✅ Set' if config.notifications.discord_webhook else '❌ Not set'}"
        )
        print(f"   - Email enabled: {config.notifications.email.enabled}")
        print(f"   - Pipeline timeout: {config.pipeline.timeout} seconds")

        # Cleanup
        temp_config.unlink()

    except Exception as e:
        print(f"❌ Environment variable demo error: {e}")
    finally:
        # Clean up environment variables
        for key in [
            "AUTOMATION_DISCORD_WEBHOOK",
            "AUTOMATION_EMAIL_ENABLED",
            "AUTOMATION_PIPELINE_TIMEOUT",
        ]:
            os.environ.pop(key, None)


def demo_validation():
    """Demonstrate configuration validation."""
    print("\n✅ Validation Demo")
    print("=" * 50)

    try:
        from automation.config_models import AutomationConfig, ScheduleConfig

        # Test valid configuration
        print("Testing valid configuration...")
        AutomationConfig()  # Should not raise an exception
        print("✅ Default configuration is valid")

        # Test invalid configuration
        print("\nTesting invalid configuration...")
        try:
            ScheduleConfig(frequency="daily")  # Missing required time
            print("❌ Validation should have failed!")
        except Exception as e:
            print(f"✅ Validation caught error: {e}")

        # Test time format validation
        try:
            ScheduleConfig(frequency="daily", time="25:00")  # Invalid time
            print("❌ Time validation should have failed!")
        except Exception as e:
            print(f"✅ Time validation caught error: {e}")

    except Exception as e:
        print(f"❌ Validation demo error: {e}")


def main():
    """Run all demos."""
    print("🚀 Enhanced Configuration System Demo")
    print("=====================================")
    print("This demo showcases the new configuration system implemented")
    print("as part of Phase 1 remediation based on the audit report.\n")

    # Run demos
    config = demo_configuration_loading()
    demo_template_generation()
    demo_dashboard_generation(config)
    demo_environment_variables()
    demo_validation()

    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Check the generated templates in automation/ and list_discovery/")
    print("2. Open the dashboard HTML file in your browser")
    print("3. Try setting environment variables and reloading config")
    print("4. Explore the new configuration models in automation/config_models.py")


if __name__ == "__main__":
    main()
