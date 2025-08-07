"""
Azure Key Vault Integration Demo
Demonstrates the secure credential management implementation.
"""
import os
from src.security_manager import SecurityManager, get_security_manager

def demonstrate_keyvault_integration() -> None:
    """Demonstrate the Azure Key Vault integration functionality."""
    print("=== Azure Key Vault Security Integration Demo ===\n")

    # 1. Initialize Security Manager
    print("1. Initializing Security Manager...")
    security = SecurityManager()

    # 2. Health Check
    print("2. Performing Security Manager Health Check...")
    health = security.health_check()
    print(f"   - Azure Available: {health['azure_available']}")
    print(f"   - Key Vault Configured: {health['keyvault_configured']}")
    print(f"   - Fallback Mode: {health['fallback_mode']}")

    # 3. Demonstrate Credential Retrieval (with fallback)
    print("\n3. Testing Credential Retrieval...")

    # Set some test environment variables for demo
    os.environ['TEST_API_KEY'] = 'demo-api-key-12345'
    os.environ['TEST_EMAIL_USERNAME'] = 'demo@example.com'
    os.environ['TEST_SMTP_SERVER'] = 'smtp.demo.com'

    try:
        # Test API key retrieval
        api_key = security.get_secret('test-api-key', 'TEST_API_KEY')
        print(f"   ✅ API Key Retrieved: {api_key[:8]}...")

        # Test email config retrieval
        email_config = security.get_email_config()
        if email_config:
            print(f"   ✅ Email Config Retrieved: {len(email_config)} settings")
        else:
            print("   ⚠️ Email Config Empty (using fallback)")

        # Test API config retrieval
        api_config = security.get_api_config()
        print(f"   ✅ API Config Retrieved: {len(api_config)} keys")

    except Exception as e:
        print(f"   ❌ Error retrieving credentials: {e}")

    # 4. Global Security Manager Test
    print("\n4. Testing Global Security Manager...")
    global_manager = get_security_manager()
    print(f"   ✅ Global manager initialized: {global_manager is not None}")
    print(f"   ✅ Singleton pattern working: {global_manager is get_security_manager()}")

    # 5. Migration Path Demonstration
    print("\n5. Demonstrating Migration Path...")
    print("   Before (Environment Variables):")
    print("   ```python")
    print("   import os")
    print("   api_key = os.getenv('API_KEY')")
    print("   ```")
    print("")
    print("   After (Azure Key Vault with Fallback):")
    print("   ```python")
    print("   from src.security_manager import get_security_manager")
    print("   security = get_security_manager()")
    print("   api_key = security.get_secret('api-key', 'API_KEY')")
    print("   ```")

    # 6. Security Benefits
    print("\n6. Security Benefits Achieved:")
    print("   ✅ Centralized credential management")
    print("   ✅ Azure Key Vault integration (when available)")
    print("   ✅ Graceful fallback to environment variables")
    print("   ✅ Audit logging and access tracking")
    print("   ✅ Type-safe configuration retrieval")
    print("   ✅ Caching for performance optimization")

    # Cleanup demo environment variables
    for key in ['TEST_API_KEY', 'TEST_EMAIL_USERNAME', 'TEST_SMTP_SERVER']:
        os.environ.pop(key, None)

    print("\n=== Demo Complete ===")
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
