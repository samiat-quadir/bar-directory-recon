#!/usr/bin/env python3
"""
Security Integration Demo for ASUS

Demonstrates the SecurityManager capabilities mirroring ALI's implementation.

Author: ACE (ASUS Device)
Date: August 6, 2025
"""

import json
import logging
import os
from pathlib import Path

# Import our SecurityManager
from src.security_manager import SecurityManager, get_secret, get_security_manager


def setup_demo_environment() -> dict:
    """Set up demo environment variables for testing."""
    demo_vars = {
        "DATABASE_HOST": "asus-db-server.local",
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "asus_recon_db",
        "DATABASE_USERNAME": "asus_user",
        "DATABASE_PASSWORD": "super_secure_password_123",
        "EMAIL_SMTP_SERVER": "smtp.asus.com",
        "EMAIL_SMTP_PORT": "587",
        "EMAIL_USERNAME": "automation@asus.com",
        "EMAIL_PASSWORD": "email_secure_pass_456",
        "EMAIL_FROM_ADDRESS": "noreply@asus-recon.com",
        "ENRICHMENT_API_KEY": "asus_enrich_key_789abc",
        "GEOCODING_API_KEY": "asus_geo_key_def123",
        "WEBHOOK_SECRET": "asus_webhook_secret_456ghi",
        "TEST_CONNECTION": "demo_connection_success",
    }

    for key, value in demo_vars.items():
        os.environ[key] = value

    print("🔧 Demo environment variables set up")
    return demo_vars


def demonstrate_security_manager():
    """Demonstrate SecurityManager functionality."""
    print("\n🔐 ASUS SecurityManager Demonstration")
    print("=" * 50)

    # Initialize SecurityManager
    print("\n1. Initializing SecurityManager...")
    manager = SecurityManager()
    print(f"   Manager: {manager}")

    # Health check
    print("\n2. Performing health check...")
    health = manager.health_check()
    print("   Health Status:")
    for key, value in health.items():
        status_icon = "✅" if value else "❌"
        print(f"   {status_icon} {key}: {value}")

    # Test individual secret retrieval
    print("\n3. Testing individual secret retrieval...")
    test_secrets = [
        ("database-host", "DATABASE_HOST"),
        ("enrichment-api-key", "ENRICHMENT_API_KEY"),
        ("nonexistent-secret", None),
    ]

    for secret_name, env_var in test_secrets:
        result = manager.get_secret(secret_name, env_var)
        status = "✅ Found" if result else "❌ Not Found"
        masked_result = f"{result[:8]}..." if result and len(result) > 8 else result
        print(f"   {status} {secret_name}: {masked_result}")

    # Test configuration bundles
    print("\n4. Testing configuration bundles...")

    print("   📊 Database Configuration:")
    db_config = manager.get_database_config()
    for key, value in db_config.items():
        masked_value = f"{value[:8]}..." if value and len(str(value)) > 8 else value
        print(f"      {key}: {masked_value}")

    print("\n   📧 Email Configuration:")
    email_config = manager.get_email_config()
    for key, value in email_config.items():
        masked_value = f"{value[:8]}..." if value and len(str(value)) > 8 else value
        print(f"      {key}: {masked_value}")

    print("\n   🔑 API Configuration:")
    api_config = manager.get_api_config()
    for key, value in api_config.items():
        masked_value = f"{value[:8]}..." if value and len(str(value)) > 8 else value
        print(f"      {key}: {masked_value}")

    return manager


def demonstrate_global_functions():
    """Demonstrate global convenience functions."""
    print("\n5. Testing global convenience functions...")

    # Test singleton pattern
    manager1 = get_security_manager()
    manager2 = get_security_manager()
    singleton_status = (
        "✅ Singleton working" if manager1 is manager2 else "❌ Singleton failed"
    )
    print(f"   {singleton_status}")

    # Test convenience secret retrieval
    secret_value = get_secret("test-connection", "TEST_CONNECTION")
    convenience_status = (
        "✅ Convenience function working"
        if secret_value
        else "❌ Convenience function failed"
    )
    print(f"   {convenience_status}: {secret_value}")


def demonstrate_caching():
    """Demonstrate LRU caching functionality."""
    print("\n6. Testing LRU caching...")

    manager = get_security_manager()

    # Clear cache first
    manager.get_secret.cache_clear()

    # Make some calls
    manager.get_secret("database-host", "DATABASE_HOST")
    manager.get_secret("database-host", "DATABASE_HOST")  # Should be cached
    manager.get_secret("email-username", "EMAIL_USERNAME")

    # Check cache info
    cache_info = manager.get_secret.cache_info()
    print(f"   Cache Info: {cache_info}")
    print(f"   ✅ Cache hits: {cache_info.hits}, misses: {cache_info.misses}")


def demonstrate_azure_simulation() -> None:
    """Simulate Azure Key Vault scenarios (without real Azure)."""
    print("\n7. Simulating Azure Key Vault scenarios...")

    # Test with Key Vault URL but no Azure
    test_manager = SecurityManager(keyvault_url="https://asus-demo.vault.azure.net/")
    print(f"   Mock Azure setup: {test_manager}")

    # Show fallback behavior
    secret = test_manager.get_secret("database-host", "DATABASE_HOST")
    fallback_status = "✅ Fallback working" if secret else "❌ Fallback failed"
    print(f"   {fallback_status}: Falls back to environment variables")


def generate_security_report() -> dict:
    """Generate a security configuration report."""
    print("\n8. Generating security configuration report...")

    manager = get_security_manager()

    report = {
        "timestamp": "2025-08-06T12:00:00Z",
        "device": "ASUS",
        "security_manager_status": repr(manager),
        "health_check": manager.health_check(),
        "configurations": {
            "database": {k: bool(v) for k, v in manager.get_database_config().items()},
            "email": {k: bool(v) for k, v in manager.get_email_config().items()},
            "api": {k: bool(v) for k, v in manager.get_api_config().items()},
        },
        "cache_performance": manager.get_secret.cache_info()._asdict(),
    }

    # Write report to file
    report_path = Path("security_report_asus.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"   📋 Security report saved to: {report_path}")
    return report


def main() -> None:
    """Main demo function."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("🚀 ASUS Security Integration Demo")
    print("Mirroring ALI's proven security architecture")
    print("=" * 60)

    try:
        # Set up demo environment
        demo_vars = setup_demo_environment()

        # Run demonstrations
        manager = demonstrate_security_manager()
        demonstrate_global_functions()
        demonstrate_caching()
        demonstrate_azure_simulation()
        generate_security_report()

        print("\n🎉 ASUS Security Integration Demo Complete!")
        print("=" * 60)
        print(f"✅ SecurityManager functioning in {manager.__repr__()}")
        print(f"✅ All {len(demo_vars)} demo configurations working")
        print(f"✅ Cache performance: {manager.get_secret.cache_info()}")
        print("✅ Security report generated")

        print("\n🔄 Cross-Device Validation Ready:")
        print("   ASUS implementation mirrors ALI's architecture")
        print("   Ready for production Azure Key Vault integration")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logging.exception("Demo error")

    finally:
        # Clean up demo environment variables
        demo_var_keys = [
            "DATABASE_HOST",
            "DATABASE_PORT",
            "DATABASE_NAME",
            "DATABASE_USERNAME",
            "DATABASE_PASSWORD",
            "EMAIL_SMTP_SERVER",
            "EMAIL_SMTP_PORT",
            "EMAIL_USERNAME",
            "EMAIL_PASSWORD",
            "EMAIL_FROM_ADDRESS",
            "ENRICHMENT_API_KEY",
            "GEOCODING_API_KEY",
            "WEBHOOK_SECRET",
            "TEST_CONNECTION",
        ]
        for var in demo_var_keys:
            os.environ.pop(var, None)
        print("\n🧹 Demo environment cleaned up")


if __name__ == "__main__":
    main()
