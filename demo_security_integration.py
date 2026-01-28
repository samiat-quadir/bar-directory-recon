#!/usr/bin/env python3
"""
Security Integration Demo
Demonstrates the SecurityManager capabilities for secure credential management.
"""

import logging
import os

# Import our SecurityManager
from src.security_manager import get_secret, get_security_manager


def setup_demo_environment() -> dict:
    """Set up demo environment variables for testing."""
    demo_vars = {
        "DATABASE_HOST": "demo-db-server.local",
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "demo_recon_db",
        "DATABASE_USERNAME": "demo_user",
        "DATABASE_PASSWORD": "PLACEHOLDER_DB_PASS",  # pragma: allowlist secret
        "EMAIL_SMTP_SERVER": "smtp.demo.com",
        "EMAIL_SMTP_PORT": "587",
        "EMAIL_USERNAME": "automation@demo.com",
        "EMAIL_PASSWORD": "PLACEHOLDER_EMAIL_PASS",  # pragma: allowlist secret
        "EMAIL_FROM_ADDRESS": "noreply@demo-recon.com",
        "ENRICHMENT_API_KEY": "PLACEHOLDER_API_KEY",  # pragma: allowlist secret
        "GEOCODING_API_KEY": "PLACEHOLDER_GEO_KEY",  # pragma: allowlist secret
        "WEBHOOK_SECRET": "PLACEHOLDER_WEBHOOK_SECRET",  # pragma: allowlist secret
        "TEST_CONNECTION": "demo_connection_success",
    }

    for key, value in demo_vars.items():
        os.environ[key] = value

    print("🔧 Demo environment variables set up")
    return demo_vars


def demonstrate_security_manager():
    """Demonstrate SecurityManager functionality."""
    print("\n🔐 SecurityManager Demonstration")
    print("=" * 50)

    # Initialize security manager
    security = get_security_manager()

    # 1. Health Check
    print("\n1. Security Manager Health Check")
    health = security.health_check()
    print(f"   ✅ Security Manager Status: {health}")

    # 2. Database Configuration
    print("\n2. Database Configuration Retrieval")
    db_config = security.get_database_config()
    print(f"   ✅ Database Config Retrieved: {db_config['host']}")

    # 3. Email Configuration
    print("\n3. Email Configuration Retrieval")
    email_config = security.get_email_config()
    print(f"   ✅ Email Config Retrieved: {email_config['smtp_server']}")

    # 4. API Configuration
    print("\n4. API Configuration Retrieval")
    api_config = security.get_api_config()
    print(f"   ✅ API Config Retrieved: {len(api_config)} keys")

    # 5. Individual Secret Retrieval
    print("\n5. Individual Secret Retrieval")
    webhook_secret = get_secret("WEBHOOK_SECRET", "default_webhook")
    if webhook_secret:
        print(f"   ✅ Webhook Secret Retrieved: {webhook_secret[:10]}...")
    else:
        print("   ⚠️ Webhook Secret not found")

    return True


def demonstrate_azure_integration():
    """Demonstrate Azure Key Vault integration if available."""
    print("\n☁️ Azure Key Vault Integration Test")
    print("=" * 50)

    security = get_security_manager()

    # Check if Azure is available
    health = security.health_check()
    if health.get("azure_available"):
        print("   ✅ Azure SDK Available")
        print("   ✅ Key Vault Integration Ready")
    else:
        print("   ⚠️ Azure SDK Not Available - Using Environment Fallback")

if __name__ == "__main__":
    main()

def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n🛡️ Error Handling Demonstration")
    print("=" * 50)

    security = get_security_manager()

    # Try to get a non-existent secret
    result = security.get_secret("NON_EXISTENT_SECRET", "fallback_value")
    print(f"   ✅ Non-existent secret handled: {result}")

    # Test with None fallback
    result = security.get_secret("ANOTHER_NON_EXISTENT", None)
    print(f"   ✅ None fallback handled: {result}")

    return True


def cleanup_demo_environment():
    """Clean up demo environment variables."""
    print("\n🧹 Cleaning up demo environment")
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
    print("🧹 Demo environment cleaned up")


def main():
    """Main demonstration function."""
    print("🚀 Security Integration Demo")
    print("=" * 60)

    try:
        # Setup demo environment
        setup_demo_environment()

        # Run demonstrations
        demonstrate_security_manager()
        demonstrate_azure_integration()
        demonstrate_error_handling()

        print("\n🎉 All demonstrations completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logging.exception("Demo error")

    finally:
        # Always cleanup
        cleanup_demo_environment()


if __name__ == "__main__":
    main()
