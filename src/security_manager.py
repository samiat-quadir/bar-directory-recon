"""
Azure Key Vault Security Manager

This module provides secure credential management using Azure Key Vault,
replacing environment variable-based credential storage.
"""
import logging
import os
from typing import Optional, Dict, Any
from functools import lru_cache

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure Key Vault dependencies not installed. Using fallback mode.")


class SecurityManager:
    """
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
