
#!/usr/bin/env python3
"""
Security Manager for Azure Key Vault Integration

This module provides secure credential management using Azure Key Vault
with graceful fallback to environment va            "host        return {
              return {
            "e        # Test a simple secret retrieval if possible
        if self._connection_healthy:
            try:
                test_result = self.get_secret(
                    "test-connection", "TEST_CONNECTION"
                )
                status["test_retrieval"] = (
                    "success" if test_result is not None else "no_secret"
                )
            except Exception as e:
                status["test_retrieval"] = f"failed: {e}"nt_api_key": self.get_secret(
                "enrichment-api-key", "ENRICHMENT_API_KEY"
            ),
            "geocoding_api_key": self.get_secret(
                "geocoding-api-key", "GEOCODING_API_KEY"
            ),
            "webhook_secret": self.get_secret(
                "webhook-secret", "WEBHOOK_SECRET"
            ),
        } "smtp_server": self.get_secret(
                "email-smtp-server", "EMAIL_SMTP_SERVER"
            ),
            "smtp_port": self.get_secret(
                "email-smtp-port", "EMAIL_SMTP_PORT"
            )
            or "587",
            "username": self.get_secret("email-username", "EMAIL_USERNAME"),
            "password": self.get_secret("email-password", "EMAIL_PASSWORD"),
            "from_address": self.get_secret(
                "email-from-address", "EMAIL_FROM_ADDRESS"
            ),
        }.get_secret("database-host", "DATABASE_HOST"),
            "port": self.get_secret("database-port", "DATABASE_PORT") or "5432",
            "name": self.get_secret("database-name", "DATABASE_NAME"),
            "username": self.get_secret(
                "database-username", "DATABASE_USERNAME"
            ),
            "password": self.get_secret(
                "database-password", "DATABASE_PASSWORD"
This module provides secure credential management using Azure Key Vault,
with graceful fallback to environment variables for development scenarios.

Mirrors the implementation from ALI (Alienware) with ASUS-specific adaptations.

Author: ACE (ASUS Device)
Date: August 6, 2025
"""

import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional, Union

try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning(
        "Azure SDK not available. Falling back to environment variables only."
    )
=======
"""
Azure Key Vault Security Manager

This module provides secure credential management using Azure Key Vault,
replacing environment variable-based credential storage.
"""
import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional

try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure Key Vault dependencies not installed. Using fallback mode.")


class SecurityManager:
    """
    Azure Key Vault integration with environment variable fallback.

    This class mirrors ALI's proven architecture for secure credential management
    across development and production environments.
    """

    def __init__(
        self,
        keyvault_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize SecurityManager with Azure Key Vault integration.

        Args:
            keyvault_url: Azure Key Vault URL
                (e.g., https://vault.vault.azure.net/)
            tenant_id: Azure tenant ID for service principal auth
            client_id: Azure client ID for service principal auth
            client_secret: Azure client secret for service principal auth
        """
        self.logger = logging.getLogger(__name__)
        self.keyvault_url = keyvault_url or os.getenv("AZURE_KEYVAULT_URL")
        self.client: Optional[SecretClient] = None
        self._connection_healthy = False

        if AZURE_AVAILABLE and self.keyvault_url:
            self._initialize_azure_client(tenant_id, client_id, client_secret)
        else:
            self.logger.info(
                "Using environment variable fallback for credential management"
            )

    def _initialize_azure_client(
        self,
        tenant_id: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
    ) -> None:
        """Initialize Azure Key Vault client with authentication."""
        try:
            # Ensure keyvault_url is available
            if not self.keyvault_url:
                self.logger.error(
                    "Key Vault URL is required for Azure client initialization"
                )
                return

            # Try service principal authentication first
            if all([tenant_id, client_id, client_secret]):
                self.logger.info(
                    "Initializing SecurityManager with service principal auth"
                )
                credential: Union[ClientSecretCredential, DefaultAzureCredential] = (
                    ClientSecretCredential(
                        tenant_id=str(tenant_id),
                        client_id=str(client_id),
                        client_secret=str(client_secret),
                    )
                )
            else:
                self.logger.info(
                    "Initializing SecurityManager with default credential chain"
                )
                credential = DefaultAzureCredential()

            self.client = SecretClient(
                vault_url=self.keyvault_url, credential=credential
            )

            # Test connection
            self._test_connection()

        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Key Vault client: {e}")
            self.client = None

    def _test_connection(self) -> bool:
        """Test Azure Key Vault connectivity."""
        if not self.client:
            return False

        try:
            # Try to list secrets to test connection (just check if we can connect)
            list(self.client.list_properties_of_secrets())
            self._connection_healthy = True
            self.logger.info("Azure Key Vault connection successful")
            return True
        except Exception as e:
            self.logger.warning(f"Azure Key Vault connection test failed: {e}")
            self._connection_healthy = False
            return False

    @lru_cache(maxsize=128)
    def get_secret(
        self, secret_name: str, fallback_env_var: Optional[str] = None
    ) -> Optional[str]:
        """
        Retrieve secret from Azure Key Vault with environment variable fallback.
=======
    Centralized security credential management using Azure Key Vault.

    Provides secure retrieval of sensitive credentials with fallback support
    for development environments.
    """

    def __init__(self, keyvault_url: Optional[str] = None):
        """
        Initialize the SecurityManager.

        Args:
            keyvault_url: Azure Key Vault URL. If None, reads from environment.
        """
        self.keyvault_url = keyvault_url or os.getenv('AZURE_KEYVAULT_URL')
        self.client = None
        self.fallback_mode = False

        if AZURE_AVAILABLE and self.keyvault_url:
            try:
                self._initialize_client()
            except Exception as e:
                logging.warning(f"Failed to initialize Azure Key Vault client: {e}")
                self.fallback_mode = True
        else:
            logging.warning("Azure Key Vault not configured. Operating in fallback mode.")
            self.fallback_mode = True

    def _initialize_client(self):
        """Initialize the Azure Key Vault client with appropriate credentials."""
        try:
            # Try service principal authentication first
            client_id = os.getenv('AZURE_CLIENT_ID')
            client_secret = os.getenv('AZURE_CLIENT_SECRET')
            tenant_id = os.getenv('AZURE_TENANT_ID')

            if client_id and client_secret and tenant_id:
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
                logging.info("Using service principal authentication for Key Vault")
            else:
                # Fall back to default credential chain
                credential = DefaultAzureCredential()
                logging.info("Using default credential chain for Key Vault")

            self.client = SecretClient(
                vault_url=self.keyvault_url,
                credential=credential
            )

            # Test connection
            list(self.client.list_properties_of_secrets(max_page_size=1))
            logging.info("Successfully connected to Azure Key Vault")

        except Exception as e:
            logging.error(f"Failed to initialize Key Vault client: {e}")
            raise

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str, fallback_env_var: Optional[str] = None) -> str:
        """
        Retrieve a secret from Azure Key Vault with fallback support.

        Args:
            secret_name: Name of the secret in Key Vault
            fallback_env_var: Environment variable name for fallback

        Returns:
            Secret value or None if not found
        """
        # Try Azure Key Vault first
        if self.client and self._connection_healthy:
            try:
                secret = self.client.get_secret(secret_name)
                self.logger.debug(
                    f"Retrieved secret '{secret_name}' from Azure Key Vault"
                )
                return secret.value
            except Exception as e:
                self.logger.warning(
                    f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}"
                )

        # Fallback to environment variable
        env_var = fallback_env_var or self._convert_secret_name_to_env_var(secret_name)
        value = os.getenv(env_var)

        if value:
            self.logger.debug(
                f"Retrieved secret '{secret_name}' from environment "
                f"variable '{env_var}'"
            )
            return value

        self.logger.warning(
            f"Secret '{secret_name}' not found in Key Vault or "
            f"environment variables"
        )
        return None

    def _convert_secret_name_to_env_var(self, secret_name: str) -> str:
        """
        Convert Key Vault secret name to environment variable format.

        Example: 'api-key' -> 'API_KEY'
        """
        return secret_name.replace("-", "_").replace(" ", "_").upper()

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration from secrets."""
        return {
            "host": self.get_secret("database-host", "DATABASE_HOST"),
            "port": self.get_secret("database-port", "DATABASE_PORT") or "5432",
            "name": self.get_secret("database-name", "DATABASE_NAME"),
            "username": self.get_secret("database-username", "DATABASE_USERNAME"),
            "password": self.get_secret("database-password", "DATABASE_PASSWORD"),
        }

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration from secrets."""
        return {
            "smtp_server": self.get_secret("email-smtp-server", "EMAIL_SMTP_SERVER"),
            "smtp_port": self.get_secret("email-smtp-port", "EMAIL_SMTP_PORT") or "587",
            "username": self.get_secret("email-username", "EMAIL_USERNAME"),
            "password": self.get_secret("email-password", "EMAIL_PASSWORD"),
            "from_address": self.get_secret("email-from-address", "EMAIL_FROM_ADDRESS"),
        }

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration from secrets."""
        return {
            "enrichment_api_key": self.get_secret(
                "enrichment-api-key", "ENRICHMENT_API_KEY"
            ),
            "geocoding_api_key": self.get_secret(
                "geocoding-api-key", "GEOCODING_API_KEY"
            ),
            "webhook_secret": self.get_secret("webhook-secret", "WEBHOOK_SECRET"),
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on security manager.

        Returns:
            Health status information
        """
        status: Dict[str, Any] = {
            "azure_available": AZURE_AVAILABLE,
            "keyvault_configured": bool(self.keyvault_url),
            "client_initialized": bool(self.client),
            "connection_healthy": self._connection_healthy,
            "fallback_mode": not self._connection_healthy,
        }

        # Test a simple secret retrieval if possible
        if self._connection_healthy:
            try:
                test_result = self.get_secret("test-connection", "TEST_CONNECTION")
                status["test_retrieval"] = (
                    "success" if test_result is not None else "no_secret"
                )
            except Exception as e:
                status["test_retrieval"] = f"failed: {e}"

        return status

    def __repr__(self) -> str:
        """String representation of SecurityManager."""
        mode = (
            "Azure Key Vault" if self._connection_healthy else "Environment Variables"
        )
        return f"SecurityManager(mode={mode}, healthy={self._connection_healthy})"


# Global instance for easy access
_security_manager: Optional[SecurityManager] = None


def get_security_manager(**kwargs: Any) -> SecurityManager:
    """
    Get or create global SecurityManager instance.

    This follows the singleton pattern for efficient credential management.
    """
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(**kwargs)
    return _security_manager


def get_secret(
    secret_name: str, fallback_env_var: Optional[str] = None
) -> Optional[str]:
    """
    Convenience function to get a secret using the global SecurityManager.

    Args:
        secret_name: Name of the secret
        fallback_env_var: Environment variable fallback

    Returns:
        Secret value or None
    """
    manager = get_security_manager()
    return manager.get_secret(secret_name, fallback_env_var)


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)

    print("🔐 ASUS SecurityManager Demo")
    print("=" * 40)

    # Initialize security manager
    manager = SecurityManager()
    print(f"Security Manager: {manager}")

    # Health check
    health = manager.health_check()
    print(f"\nHealth Status: {json.dumps(health, indent=2)}")

    # Test configuration retrieval
    print("\nTesting configuration retrieval...")
    api_config = manager.get_api_config()
    print(f"API Config keys: {list(api_config.keys())}")

    print("\n✅ SecurityManager demo complete!")
=======
            Secret value as string

        Raises:
            ValueError: If secret not found and no fallback available
        """
        # Try Azure Key Vault first
        if not self.fallback_mode and self.client:
            try:
                secret = self.client.get_secret(secret_name)
                logging.debug(f"Retrieved secret '{secret_name}' from Key Vault")
                return secret.value
            except Exception as e:
                logging.warning(f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}")

        # Fallback to environment variable
        if fallback_env_var:
            env_value = os.getenv(fallback_env_var)
            if env_value:
                logging.warning(f"Using fallback environment variable for '{secret_name}'")
                return env_value

        # Try converting secret name to environment variable format
        env_var_name = secret_name.upper().replace('-', '_')
        env_value = os.getenv(env_var_name)
        if env_value:
            logging.warning(f"Using fallback environment variable '{env_var_name}' for '{secret_name}'")
            return env_value

        raise ValueError(f"Secret '{secret_name}' not found in Key Vault or environment variables")

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration from secure storage."""
        try:
            return {
                'smtp_server': self.get_secret('smtp-server', 'SMTP_SERVER'),
                'smtp_port': int(self.get_secret('smtp-port', 'SMTP_PORT')),
                'username': self.get_secret('email-username', 'EMAIL_USERNAME'),
                'password': self.get_secret('email-password', 'EMAIL_PASSWORD'),
                'from_email': self.get_secret('from-email', 'FROM_EMAIL'),
                'to_emails': self.get_secret('to-emails', 'TO_EMAILS').split(',')
            }
        except (ValueError, TypeError) as e:
            logging.error(f"Failed to retrieve email configuration: {e}")
            return {}

    def get_api_config(self) -> Dict[str, str]:
        """Get API configuration from secure storage."""
        config = {}

        api_keys = [
            ('hunter_api_key', 'hunter-api-key', 'HUNTER_API_KEY'),
            ('zerobounce_api_key', 'zerobounce-api-key', 'ZEROBOUNCE_API_KEY'),
            ('twilio_account_sid', 'twilio-account-sid', 'TWILIO_ACCOUNT_SID'),
            ('twilio_auth_token', 'twilio-auth-token', 'TWILIO_AUTH_TOKEN'),
            ('discord_webhook', 'discord-webhook-url', 'DISCORD_WEBHOOK_URL'),
            ('slack_webhook', 'slack-webhook-url', 'SLACK_WEBHOOK_URL')
        ]

        for config_key, secret_name, env_var in api_keys:
            try:
                config[config_key] = self.get_secret(secret_name, env_var)
            except ValueError:
                logging.debug(f"API key '{secret_name}' not found, skipping")
                pass

        return config

    def get_google_sheets_config(self) -> Dict[str, str]:
        """Get Google Sheets configuration from secure storage."""
        try:
            return {
                'credentials_path': self.get_secret('google-sheets-credentials', 'GOOGLE_SHEETS_CREDENTIALS_PATH'),
                'sheet_id': self.get_secret('google-sheets-id', 'SHEET_ID')
            }
        except ValueError as e:
            logging.error(f"Failed to retrieve Google Sheets configuration: {e}")
            return {}

    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration from secure storage."""
        try:
            return {
                'url': self.get_secret('database-url', 'DATABASE_URL'),
                'password': self.get_secret('database-password', 'DATABASE_PASSWORD')
            }
        except ValueError as e:
            logging.error(f"Failed to retrieve database configuration: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the security manager.

        Returns:
            Dictionary with health status information
        """
        status = {
            'azure_available': AZURE_AVAILABLE,
            'keyvault_configured': bool(self.keyvault_url),
            'client_initialized': bool(self.client),
            'fallback_mode': self.fallback_mode,
            'timestamp': logging.time.time()
        }

        if self.client:
            try:
                # Test Key Vault connectivity
                list(self.client.list_properties_of_secrets(max_page_size=1))
                status['keyvault_accessible'] = True
            except Exception as e:
                status['keyvault_accessible'] = False
                status['keyvault_error'] = str(e)

        return status


# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get the global SecurityManager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Convenience functions for backward compatibility
def get_secret(secret_name: str, fallback_env_var: Optional[str] = None) -> str:
    """Convenience function to get a secret."""
    return get_security_manager().get_secret(secret_name, fallback_env_var)


def get_email_config() -> Dict[str, Any]:
    """Convenience function to get email configuration."""
    return get_security_manager().get_email_config()


def get_api_config() -> Dict[str, str]:
    """Convenience function to get API configuration."""
    return get_security_manager().get_api_config()
