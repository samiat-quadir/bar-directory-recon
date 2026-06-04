"""
Unit tests for DataHunter module.

Tests cover:
- _get_file_hash: SHA-256 hash generation
- _load_config: Config loading with/without existing file
"""

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_hunter import DataHunter  # noqa: E402


class TestDataHunterGetFileHash:
    """Test cases for DataHunter._get_file_hash method."""

    def test_get_file_hash_returns_sha256(self, tmp_path):
        """Test that _get_file_hash returns correct SHA-256 hash."""
        # Setup: Create a minimal config file to avoid side effects
        config_path = tmp_path / "config" / "test_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text('{}')

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Known test case: SHA-256 of "https://example.com/test.pdf"
        test_url = "https://example.com/test.pdf"

        result = hunter._get_file_hash(test_url)

        # SHA-256 produces 64 character hex digest
        assert len(result) == 64
        assert result.isalnum()  # Should be hex characters only
        # Verify it's deterministic
        assert result == hunter._get_file_hash(test_url)

    def test_get_file_hash_different_inputs_different_hashes(self, tmp_path):
        """Test that different URLs produce different hashes."""
        config_path = tmp_path / "config" / "test_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text('{}')

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        url1 = "https://example.com/file1.pdf"
        url2 = "https://example.com/file2.pdf"

        hash1 = hunter._get_file_hash(url1)
        hash2 = hunter._get_file_hash(url2)

        assert hash1 != hash2

    def test_get_file_hash_known_value(self, tmp_path):
        """Test hash against known SHA-256 value."""
        config_path = tmp_path / "config" / "test_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text('{}')

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Pre-computed SHA-256 hash for "test"
        test_string = "test"
        expected = hashlib.sha256(test_string.encode()).hexdigest()

        result = hunter._get_file_hash(test_string)

        assert result == expected


class TestDataHunterLoadConfig:
    """Test cases for DataHunter._load_config method."""

    def test_load_config_creates_default_when_missing(self, tmp_path):
        """Test that _load_config creates default config when file doesn't exist."""
        config_path = tmp_path / "config" / "nonexistent_config.json"

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Verify default config was created
        assert config_path.exists()

        # Verify essential default keys exist
        assert 'sources' in hunter.config
        assert 'notifications' in hunter.config
        assert 'download_settings' in hunter.config
        assert 'schedule' in hunter.config

        # Verify default sources exist
        assert len(hunter.config['sources']) > 0

    def test_load_config_loads_existing_file(self, tmp_path):
        """Test that _load_config loads existing configuration file."""
        config_path = tmp_path / "config" / "existing_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        custom_config = {
            "sources": [
                {
                    "name": "Test-Source",
                    "url": "https://test.example.com",
                    "patterns": [r".*test.*\.pdf"],
                    "enabled": True,
                    "check_frequency_hours": 12
                }
            ],
            "notifications": {
                "console": {"enabled": True}
            },
            "download_settings": {
                "max_file_size_mb": 100,
                "timeout_seconds": 60
            }
        }

        config_path.write_text(json.dumps(custom_config))

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Verify custom values were loaded
        assert hunter.config['sources'][0]['name'] == "Test-Source"
        assert hunter.config['download_settings']['max_file_size_mb'] == 100
        assert hunter.config['download_settings']['timeout_seconds'] == 60

    def test_load_config_merges_with_defaults(self, tmp_path):
        """Test that _load_config merges loaded config with defaults."""
        config_path = tmp_path / "config" / "partial_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Partial config missing some keys
        partial_config = {
            "sources": [
                {
                    "name": "Custom-Source",
                    "url": "https://custom.example.com",
                    "patterns": [],
                    "enabled": True
                }
            ]
        }

        config_path.write_text(json.dumps(partial_config))

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Verify custom source was loaded
        assert hunter.config['sources'][0]['name'] == "Custom-Source"

        # Verify defaults were merged for missing keys
        assert 'notifications' in hunter.config
        assert 'download_settings' in hunter.config
        assert 'schedule' in hunter.config

    def test_load_config_handles_invalid_json(self, tmp_path):
        """Test that _load_config falls back to defaults on invalid JSON."""
        config_path = tmp_path / "config" / "invalid_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write invalid JSON
        config_path.write_text("{ invalid json content }")

        with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
            hunter = DataHunter(config_path=str(config_path))

        # Should fall back to defaults
        assert 'sources' in hunter.config
        assert len(hunter.config['sources']) > 0


class TestDataHunterDirectories:
    """Test directory creation behavior."""

    def test_creates_required_directories(self, tmp_path):
        """Test that DataHunter creates input and logs directories."""
        config_path = tmp_path / "config" / "test_config.json"

        # Change working directory to tmp_path to test directory creation
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            with patch.object(DataHunter, '_setup_logging', return_value=MagicMock()):
                hunter = DataHunter(config_path=str(config_path))

            # Verify directories were created
            assert hunter.input_dir.exists()
            assert hunter.logs_dir.exists()

        finally:
            os.chdir(original_cwd)
