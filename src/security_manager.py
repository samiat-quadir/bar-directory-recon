"""Security Manager for Azure Key Vault integration with fallback.

This module exposes a minimal API used by the test-suite:
  * SecurityManager (with attributes: keyvault_url, client, fallback_mode)
  * get_secret() that raises ValueError when secret missing
  * get_email_config(), get_api_config(), get_google_sheets_config(), get_database_config()
  * health_check() returning keys asserted in tests
  * Global singleton helpers (get_security_manager, get_secret convenience)

It resolves merge conflicts between two prior divergent implementations and
keeps behavior aligned with the expectations in tests under
`src/tests/test_security_manager.py`.
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
            ),es for development scenarios.


from __future__ import annotations

import logging
import os
import time
from functools import lru_cache
from typing import Any, Dict, Optional

try:  # Optional Azure dependencies
    from azure.identity import ClientSecretCredential, DefaultAzureCredential  # type: ignore
    from azure.keyvault.secrets import SecretClient  # type: ignore

    AZURE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):  # pragma: no cover - safety net
    AZURE_AVAILABLE = False
    # Create placeholder classes for testing when Azure SDK not available
    class ClientSecretCredential:  # type: ignore
        def __init__(self, tenant_id=None, client_id=None, client_secret=None):
            pass
    class DefaultAzureCredential:  # type: ignore
        pass
    class SecretClient:  # type: ignore
        def __init__(self, vault_url=None, credential=None):
            pass
        def get_secret(self, name):
            class MockSecret:
                value = "mock_secret_value"
            return MockSecret()
        def list_properties_of_secrets(self, max_page_size=None):
            return []
    # Delay logging setup until configured by application/tests
    logging.getLogger(__name__).warning(
        "Azure Key Vault dependencies not installed. Operating in fallback mode."
    )

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
    """Centralized credential retrieval with Key Vault + env fallback."""

    def __init__(self, keyvault_url: Optional[str] = None):
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

        self.fallback_mode = False
        if AZURE_AVAILABLE and self.keyvault_url:
            try:
                self._initialize_client()
            except Exception as e:  # pragma: no cover - defensive
                logging.warning(
                    f"Failed to initialize Azure Key Vault client: {e}. Fallback mode."
                )
                self.fallback_mode = True
        else:
            self.fallback_mode = True

    # --- Internal helpers -----------------------------------------------------------------
    def _initialize_client(self) -> None:
        if not AZURE_AVAILABLE:  # Should not be called, safety
            raise RuntimeError(
                "SecurityManager._initialize_client() called when Azure SDK is not available (AZURE_AVAILABLE=False). "
                "This indicates a bug in the caller logic. Please ensure AZURE_AVAILABLE is checked before calling this method."
            )
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        if client_id and client_secret and tenant_id:
            credential = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
            )
            logging.info("Using service principal authentication for Key Vault")
        else:
            credential = DefaultAzureCredential()
            logging.info("Using default credential chain for Key Vault")
        self.client = SecretClient(vault_url=self.keyvault_url, credential=credential)  # type: ignore[arg-type]
        # Light connectivity probe (single page) – exceptions bubble up
        list(self.client.list_properties_of_secrets(max_page_size=1))  # type: ignore[call-arg]
        logging.info("Successfully connected to Azure Key Vault")

    # --- Public API ------------------------------------------------------------------------
    @lru_cache(maxsize=128)
    def get_secret(
        self, secret_name: str, fallback_env_var: Optional[str] = None
    ) -> str:
        """Retrieve secret or raise ValueError if unavailable."""
        # Key Vault first
        if not self.fallback_mode and self.client:
            try:
                secret = self.client.get_secret(secret_name)
                return secret.value  # type: ignore[attr-defined]
            except Exception as e:  # pragma: no cover - network/azure variability
                logging.warning(
                    f"Key Vault retrieval failed for '{secret_name}': {e}; falling back"
                )

        # Named fallback env var
        if fallback_env_var:
            val = os.getenv(fallback_env_var)
            if val:
                return val

        # Auto-convert secret name -> ENV style
        auto_env = secret_name.upper().replace("-", "_")
        val2 = os.getenv(auto_env)
        if val2:
            return val2

        raise ValueError(
            f"Secret '{secret_name}' not found in Key Vault or environment variables"
        )

    def get_email_config(self) -> Dict[str, Any]:
        try:
            return {
                "smtp_server": self.get_secret("smtp-server", "SMTP_SERVER"),
                "smtp_port": int(self.get_secret("smtp-port", "SMTP_PORT")),
                "username": self.get_secret("email-username", "EMAIL_USERNAME"),
                "password": self.get_secret("email-password", "EMAIL_PASSWORD"),
                "from_email": self.get_secret("from-email", "FROM_EMAIL"),
                "to_emails": self.get_secret("to-emails", "TO_EMAILS").split(","),
            }
        except (ValueError, TypeError) as e:
            logging.error(f"Failed to retrieve email configuration: {e}")
            return {}

    def get_api_config(self) -> Dict[str, str]:
        mapping = [
            ("hunter_api_key", "hunter-api-key", "HUNTER_API_KEY"),
            ("zerobounce_api_key", "zerobounce-api-key", "ZEROBOUNCE_API_KEY"),
            ("twilio_account_sid", "twilio-account-sid", "TWILIO_ACCOUNT_SID"),
            ("twilio_auth_token", "twilio-auth-token", "TWILIO_AUTH_TOKEN"),
            ("discord_webhook", "discord-webhook-url", "DISCORD_WEBHOOK_URL"),
            ("slack_webhook", "slack-webhook-url", "SLACK_WEBHOOK_URL"),
        ]
        cfg: Dict[str, str] = {}
        for key, secret_name, env_var in mapping:
            try:
                cfg[key] = self.get_secret(secret_name, env_var)
            except ValueError:
                logging.debug(f"API key '{secret_name}' not present; skipping")
        return cfg

    def get_google_sheets_config(self) -> Dict[str, str]:
        try:
            return {
                "credentials_path": self.get_secret(
                    "google-sheets-credentials", "GOOGLE_SHEETS_CREDENTIALS_PATH"
                ),
                "sheet_id": self.get_secret("google-sheets-id", "SHEET_ID"),
            }
        except ValueError as e:
            logging.error(f"Failed to retrieve Google Sheets configuration: {e}")
            return {}

    def get_database_config(self) -> Dict[str, str]:
        try:
            return {
                "url": self.get_secret("database-url", "DATABASE_URL"),
                "password": self.get_secret("database-password", "DATABASE_PASSWORD"),
            }
        except ValueError as e:
            logging.error(f"Failed to retrieve database configuration: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        
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
        if self.client and not self.fallback_mode:
            try:
                list(self.client.list_properties_of_secrets(max_page_size=1))
                status["keyvault_accessible"] = True
            except Exception as e:  # pragma: no cover - network variability
                status["keyvault_accessible"] = False
                status["keyvault_error"] = str(e)
        return status


# Singleton helpers -------------------------------------------------------------------------
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def get_secret(secret_name: str, fallback_env_var: Optional[str] = None) -> str:
    return get_security_manager().get_secret(secret_name, fallback_env_var)
