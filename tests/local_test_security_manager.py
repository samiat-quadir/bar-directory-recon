#!/usr/bin/env python3
"""
Test suite for SecurityManager

Mirrors ALI's comprehensive test patterns for Azure Key Vault integration.

Author: ACE (ASUS Device)
Date: August 6, 2025
"""

import os
from unittest.mock import Mock, patch

import pytest

# Import our SecurityManager
from src.security_manager import SecurityManager, get_secret, get_security_manager


class TestSecurityManager:
    """Test suite for SecurityManager class."""

    def test_init_no_azure_sdk(self):
        """Test initialization when Azure SDK is not available."""
        with patch("src.security_manager.AZURE_AVAILABLE", False):
            manager = SecurityManager()
            assert manager.client is None
            assert not manager._connection_healthy
            assert manager.keyvault_url is None

    def test_init_with_keyvault_url_env_var(self):
        """Test initialization with Key Vault URL from environment variable."""
        test_url = "https://test-vault.vault.azure.net/"
        with patch.dict(os.environ, {"AZURE_KEYVAULT_URL": test_url}):
            with patch("src.security_manager.AZURE_AVAILABLE", False):
                manager = SecurityManager()
                assert manager.keyvault_url == test_url

    def test_init_with_keyvault_url_parameter(self):
        """Test initialization with Key Vault URL parameter."""
        test_url = "https://param-vault.vault.azure.net/"
        with patch("src.security_manager.AZURE_AVAILABLE", False):
            manager = SecurityManager(keyvault_url=test_url)
            assert manager.keyvault_url == test_url

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.ClientSecretCredential")
    def test_init_with_service_principal(self, mock_credential, mock_client):
        """Test initialization with service principal authentication."""
        test_url = "https://test-vault.vault.azure.net/"
        tenant_id = "test-tenant"
        client_id = "test-client"
        client_secret = "test-secret"

        mock_credential_instance = Mock()
        mock_credential.return_value = mock_credential_instance

        mock_client_instance = Mock()
        mock_client_instance.list_properties_of_secrets.return_value = []
        mock_client.return_value = mock_client_instance

        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager(
                keyvault_url=test_url,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )

        mock_credential.assert_called_once_with(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        mock_client.assert_called_once_with(vault_url=test_url, credential=mock_credential_instance)
        assert manager._connection_healthy

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_init_with_default_credential(self, mock_credential, mock_client):
        """Test initialization with default credential chain."""
        test_url = "https://test-vault.vault.azure.net/"

        mock_credential_instance = Mock()
        mock_credential.return_value = mock_credential_instance

        mock_client_instance = Mock()
        mock_client_instance.list_properties_of_secrets.return_value = []
        mock_client.return_value = mock_client_instance

        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager(keyvault_url=test_url)

        mock_credential.assert_called_once()
        mock_client.assert_called_once_with(vault_url=test_url, credential=mock_credential_instance)
        assert manager._connection_healthy

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_init_azure_error(self, mock_credential, mock_client):
        """Test initialization handling Azure errors."""
        test_url = "https://test-vault.vault.azure.net/"

        mock_credential.side_effect = Exception("Azure connection failed")

        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager(keyvault_url=test_url)

        assert manager.client is None
        assert not manager._connection_healthy

    def test_convert_secret_name_to_env_var(self):
        """Test secret name to environment variable conversion."""
        manager = SecurityManager()

        assert manager._convert_secret_name_to_env_var("api-key") == "API_KEY"
        assert manager._convert_secret_name_to_env_var("database-password") == "DATABASE_PASSWORD"
        assert manager._convert_secret_name_to_env_var("test secret") == "TEST_SECRET"
        assert (
            manager._convert_secret_name_to_env_var("complex-name-with-spaces")
            == "COMPLEX_NAME_WITH_SPACES"
        )

    def test_get_secret_fallback_env_var(self):
        """Test getting secret from environment variable fallback."""
        with patch.dict(os.environ, {"TEST_SECRET": "env-secret-value"}):
            manager = SecurityManager()
            result = manager.get_secret("test-secret", "TEST_SECRET")
            assert result == "env-secret-value"

    def test_get_secret_auto_env_var_conversion(self):
        """Test automatic environment variable name conversion."""
        with patch.dict(os.environ, {"API_KEY": "auto-converted-value"}):
            manager = SecurityManager()
            result = manager.get_secret("api-key")
            assert result == "auto-converted-value"

    def test_get_secret_not_found(self):
        """Test getting secret that doesn't exist."""
        manager = SecurityManager()
        result = manager.get_secret("nonexistent-secret")
        assert result is None

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_get_secret_from_azure(self, mock_credential, mock_client):
        """Test getting secret from Azure Key Vault."""
        test_url = "https://test-vault.vault.azure.net/"

        mock_secret = Mock()
        mock_secret.value = "azure-secret-value"

        mock_client_instance = Mock()
        mock_client_instance.list_properties_of_secrets.return_value = []
        mock_client_instance.get_secret.return_value = mock_secret
        mock_client.return_value = mock_client_instance

        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager(keyvault_url=test_url)
            result = manager.get_secret("test-secret")

        mock_client_instance.get_secret.assert_called_once_with("test-secret")
        assert result == "azure-secret-value"

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_get_secret_azure_fallback_to_env(self, mock_credential, mock_client):
        """Test fallback to environment variable when Azure fails."""
        test_url = "https://test-vault.vault.azure.net/"

        mock_client_instance = Mock()
        mock_client_instance.list_properties_of_secrets.return_value = []
        mock_client_instance.get_secret.side_effect = Exception("Azure error")
        mock_client.return_value = mock_client_instance

        with patch.dict(os.environ, {"TEST_SECRET": "env-fallback-value"}):
            with patch("src.security_manager.AZURE_AVAILABLE", True):
                manager = SecurityManager(keyvault_url=test_url)
                result = manager.get_secret("test-secret", "TEST_SECRET")

        assert result == "env-fallback-value"

    def test_get_database_config(self):
        """Test getting database configuration."""
        env_vars = {
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "testdb",
            "DATABASE_USERNAME": "testuser",
            "DATABASE_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars):
            manager = SecurityManager()
            config = manager.get_database_config()

        assert config["host"] == "localhost"
        assert config["port"] == "5432"
        assert config["name"] == "testdb"
        assert config["username"] == "testuser"
        assert config["password"] == "testpass"

    def test_get_email_config(self):
        """Test getting email configuration."""
        env_vars = {
            "EMAIL_SMTP_SERVER": "smtp.gmail.com",
            "EMAIL_SMTP_PORT": "587",
            "EMAIL_USERNAME": "test@example.com",
            "EMAIL_PASSWORD": "testpass",
            "EMAIL_FROM_ADDRESS": "noreply@example.com",
        }

        with patch.dict(os.environ, env_vars):
            manager = SecurityManager()
            config = manager.get_email_config()

        assert config["smtp_server"] == "smtp.gmail.com"
        assert config["smtp_port"] == "587"
        assert config["username"] == "test@example.com"
        assert config["password"] == "testpass"
        assert config["from_address"] == "noreply@example.com"

    def test_get_api_config(self):
        """Test getting API configuration."""
        env_vars = {
            "ENRICHMENT_API_KEY": "enrich-key-123",
            "GEOCODING_API_KEY": "geo-key-456",
            "WEBHOOK_SECRET": "webhook-secret-789",
        }

        with patch.dict(os.environ, env_vars):
            manager = SecurityManager()
            config = manager.get_api_config()

        assert config["enrichment_api_key"] == "enrich-key-123"
        assert config["geocoding_api_key"] == "geo-key-456"
        assert config["webhook_secret"] == "webhook-secret-789"

    def test_health_check_fallback_mode(self):
        """Test health check in fallback mode."""
        manager = SecurityManager()
        health = manager.health_check()

        assert "azure_available" in health
        assert "keyvault_configured" in health
        assert "client_initialized" in health
        assert "connection_healthy" in health
        assert "fallback_mode" in health

        assert health["fallback_mode"] is True
        assert health["connection_healthy"] is False

    @patch("src.security_manager.SecretClient")
    @patch("src.security_manager.DefaultAzureCredential")
    def test_health_check_azure_mode(self, mock_credential, mock_client):
        """Test health check in Azure mode."""
        test_url = "https://test-vault.vault.azure.net/"

        mock_client_instance = Mock()
        mock_client_instance.list_properties_of_secrets.return_value = []
        mock_client.return_value = mock_client_instance

        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager(keyvault_url=test_url)
            health = manager.health_check()

        assert health["azure_available"] is True
        assert health["keyvault_configured"] is True
        assert health["client_initialized"] is True
        assert health["connection_healthy"] is True
        assert health["fallback_mode"] is False

    def test_repr(self):
        """Test string representation."""
        manager = SecurityManager()
        repr_str = repr(manager)
        assert "SecurityManager" in repr_str
        assert "Environment Variables" in repr_str
        assert "healthy=False" in repr_str


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_get_security_manager_singleton(self):
        """Test that get_security_manager returns singleton instance."""
        # Clear any existing instance
        import src.security_manager

        src.security_manager._security_manager = None

        manager1 = get_security_manager()
        manager2 = get_security_manager()

        assert manager1 is manager2

    def test_get_secret_convenience_function(self):
        """Test convenience get_secret function."""
        with patch.dict(os.environ, {"TEST_SECRET": "convenience-value"}):
            # Clear any existing instance
            import src.security_manager

            src.security_manager._security_manager = None

            result = get_secret("test-secret", "TEST_SECRET")
            assert result == "convenience-value"


class TestCaching:
    """Test LRU cache functionality."""

    def test_secret_caching(self):
        """Test that secrets are cached properly."""
        with patch.dict(os.environ, {"CACHED_SECRET": "cached-value"}):
            manager = SecurityManager()

            # First call
            result1 = manager.get_secret("cached-secret", "CACHED_SECRET")
            # Second call should be cached
            result2 = manager.get_secret("cached-secret", "CACHED_SECRET")

            assert result1 == result2 == "cached-value"

            # Check that cache info shows hits
            cache_info = manager.get_secret.cache_info()
            assert cache_info.hits >= 1


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_missing_keyvault_url_with_azure_available(self):
        """Test behavior when Azure is available but no Key Vault URL provided."""
        with patch("src.security_manager.AZURE_AVAILABLE", True):
            manager = SecurityManager()
            assert manager.client is None
            assert not manager._connection_healthy

    def test_azure_initialization_failure(self):
        """Test handling of Azure initialization failures."""
        with patch("src.security_manager.SecretClient") as mock_client:
            mock_client.side_effect = Exception("Initialization failed")

            with patch("src.security_manager.AZURE_AVAILABLE", True):
                manager = SecurityManager(keyvault_url="https://test.vault.azure.net/")
                assert manager.client is None
                assert not manager._connection_healthy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
