"""
Test suite for SecurityManager class
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.security_manager import SecurityManager, get_secret, get_security_manager


class TestSecurityManager:
    """Test cases for SecurityManager class."""

    def test_init_without_keyvault_url(self):
        """Test initialization without Key Vault URL."""
        with patch.dict(os.environ, {}, clear=True):
            manager = SecurityManager()
            assert manager.fallback_mode is True
            assert manager.client is None

    def test_init_with_keyvault_url_no_azure(self):
        """Test initialization with Key Vault URL but no Azure libraries."""
        with patch("src.security_manager.AZURE_AVAILABLE", False):
            manager = SecurityManager(keyvault_url="https://test.vault.azure.net/")
            assert manager.fallback_mode is True
            assert manager.client is None

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.ClientSecretCredential")
    def test_init_with_service_principal(self, mock_credential, mock_client):
        """Test initialization with service principal credentials."""
        with patch.dict(
            os.environ,
            {
                "AZURE_CLIENT_ID": "test-client-id",
                "AZURE_CLIENT_SECRET": "test-secret",
                "AZURE_TENANT_ID": "test-tenant",
            },
        ):
            mock_client_instance = Mock()
            mock_client_instance.list_properties_of_secrets.return_value = iter([])
            mock_client.return_value = mock_client_instance

            manager = SecurityManager(keyvault_url="https://test.vault.azure.net/")

            mock_credential.assert_called_once_with(
                tenant_id="test-tenant",
                client_id="test-client-id",
                client_secret="test-secret",
            )
            assert manager.fallback_mode is False

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_init_with_default_credential(self, mock_credential, mock_client):
        """Test initialization with default credential chain."""
        with patch.dict(os.environ, {}, clear=True):
            mock_client_instance = Mock()
            mock_client_instance.list_properties_of_secrets.return_value = iter([])
            mock_client.return_value = mock_client_instance

            manager = SecurityManager(keyvault_url="https://test.vault.azure.net/")

            mock_credential.assert_called_once()
            assert manager.fallback_mode is False

    def test_get_secret_from_keyvault(self):
        """Test retrieving secret from Key Vault."""
        manager = SecurityManager()
        mock_client = Mock()
        mock_secret = Mock()
        mock_secret.value = "test-secret-value"
        mock_client.get_secret.return_value = mock_secret

        manager.client = mock_client
        manager.fallback_mode = False

        result = manager.get_secret("test-secret")
        assert result == "test-secret-value"
        mock_client.get_secret.assert_called_once_with("test-secret")

    def test_get_secret_fallback_env_var(self):
        """Test fallback to environment variable."""
        with patch.dict(os.environ, {"TEST_SECRET": "env-secret-value"}):
            manager = SecurityManager()
            manager.fallback_mode = True

            result = manager.get_secret("test-secret", "TEST_SECRET")
            assert result == "env-secret-value"

    def test_get_secret_auto_env_var(self):
        """Test automatic environment variable conversion."""
        with patch.dict(os.environ, {"TEST_SECRET": "auto-env-value"}):
            manager = SecurityManager()
            manager.fallback_mode = True

            result = manager.get_secret("test-secret")
            assert result == "auto-env-value"

    def test_get_secret_not_found(self):
        """Test secret not found raises ValueError."""
        manager = SecurityManager()
        manager.fallback_mode = True

        with pytest.raises(ValueError, match="Secret 'nonexistent' not found"):
            manager.get_secret("nonexistent")

    def test_get_email_config(self):
        """Test retrieving email configuration."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret") as mock_get_secret:
            mock_get_secret.side_effect = [
                "smtp.test.com",
                "587",
                "test@example.com",
                "password123",
                "from@example.com",
                "to1@example.com,to2@example.com",
            ]

            result = manager.get_email_config()

            expected = {
                "smtp_server": "smtp.test.com",
                "smtp_port": 587,
                "username": "test@example.com",
                "password": "password123",
                "from_email": "from@example.com",
                "to_emails": ["to1@example.com", "to2@example.com"],
            }
            assert result == expected

    def test_get_email_config_error(self):
        """Test email configuration error handling."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret", side_effect=ValueError("Not found")):
            result = manager.get_email_config()
            assert result == {}

    def test_get_api_config(self):
        """Test retrieving API configuration."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret") as mock_get_secret:
            mock_get_secret.side_effect = [
                "hunter-key-123",
                "zerobounce-key-456",
                "twilio-sid-789",
                "twilio-token-abc",
                "https://discord.webhook",
                "https://slack.webhook",
            ]

            result = manager.get_api_config()

            expected = {
                "hunter_api_key": "hunter-key-123",
                "zerobounce_api_key": "zerobounce-key-456",
                "twilio_account_sid": "twilio-sid-789",
                "twilio_auth_token": "twilio-token-abc",
                "discord_webhook": "https://discord.webhook",
                "slack_webhook": "https://slack.webhook",
            }
            assert result == expected

    def test_get_api_config_partial(self):
        """Test API configuration with missing keys."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret") as mock_get_secret:
            mock_get_secret.side_effect = [
                "hunter-key-123",
                ValueError("Not found"),  # zerobounce key missing
                ValueError("Not found"),  # twilio sid missing
                ValueError("Not found"),  # twilio token missing
                ValueError("Not found"),  # discord webhook missing
                ValueError("Not found"),  # slack webhook missing
            ]

            result = manager.get_api_config()

            assert result == {"hunter_api_key": "hunter-key-123"}

    def test_get_google_sheets_config(self):
        """Test retrieving Google Sheets configuration."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret") as mock_get_secret:
            mock_get_secret.side_effect = ["/path/to/credentials.json", "sheet-id-123"]

            result = manager.get_google_sheets_config()

            expected = {
                "credentials_path": "/path/to/credentials.json",
                "sheet_id": "sheet-id-123",
            }
            assert result == expected

    def test_get_database_config(self):
        """Test retrieving database configuration."""
        manager = SecurityManager()
        with patch.object(manager, "get_secret") as mock_get_secret:
            mock_get_secret.side_effect = [
                "postgresql://localhost:5432/db",
                "db-password-123",
            ]

            result = manager.get_database_config()

            expected = {
                "url": "postgresql://localhost:5432/db",
                "password": "db-password-123",
            }
            assert result == expected

    def test_health_check_fallback_mode(self):
        """Test health check in fallback mode."""
        manager = SecurityManager()
        manager.fallback_mode = True

        result = manager.health_check()

        assert result["fallback_mode"] is True
        assert result["client_initialized"] is False
        assert "timestamp" in result

    def test_health_check_keyvault_accessible(self):
        """Test health check with accessible Key Vault."""
        manager = SecurityManager()
        mock_client = Mock()
        mock_client.list_properties_of_secrets.return_value = iter([])
        manager.client = mock_client
        manager.fallback_mode = False

        result = manager.health_check()

        assert result["fallback_mode"] is False
        assert result["client_initialized"] is True
        assert result["keyvault_accessible"] is True

    def test_health_check_keyvault_error(self):
        """Test health check with Key Vault error."""
        manager = SecurityManager()
        mock_client = Mock()
        mock_client.list_properties_of_secrets.side_effect = Exception("Connection failed")
        manager.client = mock_client
        manager.fallback_mode = False

        result = manager.health_check()

        assert result["keyvault_accessible"] is False
        assert result["keyvault_error"] == "Connection failed"


class TestGlobalFunctions:
    """Test global convenience functions."""

    @patch("src.security_manager._security_manager", None)
    def test_get_security_manager_singleton(self):
        """Test that get_security_manager returns singleton."""
        manager1 = get_security_manager()
        manager2 = get_security_manager()
        assert manager1 is manager2

    def test_get_secret_convenience(self):
        """Test convenience get_secret function."""
        with patch("src.security_manager.get_security_manager") as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_secret.return_value = "test-value"
            mock_get_manager.return_value = mock_manager

            result = get_secret("test-secret", "TEST_ENV_VAR")

            assert result == "test-value"
            mock_manager.get_secret.assert_called_once_with("test-secret", "TEST_ENV_VAR")


class TestIntegration:
    """Integration tests for SecurityManager."""

    def test_real_environment_fallback(self):
        """Test real environment variable fallback."""
        with patch.dict(os.environ, {"TEST_INTEGRATION_SECRET": "integration-value"}):
            manager = SecurityManager()
            result = manager.get_secret("test-integration-secret")
            assert result == "integration-value"
