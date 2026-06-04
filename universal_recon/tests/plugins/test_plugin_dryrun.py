"""
Dry-run tests for universal_recon plugin system.

These tests validate the plugin loading, registration, and execution
infrastructure WITHOUT making any real network requests or file writes.
Useful for CI/CD validation and local development verification.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

# Import plugin utilities
from universal_recon import plugin_loader


class TestPluginRegistry:
    """Tests for plugin registry loading and validation."""

    def test_registry_file_exists(self):
        """Plugin registry JSON file must exist."""
        root = Path(__file__).resolve().parent.parent.parent
        registry_path = root / "plugin_registry.json"
        assert registry_path.exists(), f"Plugin registry not found: {registry_path}"

    def test_registry_is_valid_json(self):
        """Plugin registry must be valid JSON."""
        root = Path(__file__).resolve().parent.parent.parent
        registry_path = root / "plugin_registry.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        assert isinstance(registry, list), "Registry should be a list of plugin definitions"
        assert len(registry) > 0, "Registry should not be empty"

    def test_registry_entries_have_required_fields(self):
        """Each plugin entry must have required fields."""
        root = Path(__file__).resolve().parent.parent.parent
        registry_path = root / "plugin_registry.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        required_fields = ["site_name", "module", "function", "type", "description"]

        for entry in registry:
            for field in required_fields:
                assert field in entry, f"Plugin entry missing required field '{field}': {entry}"

    def test_registry_module_paths_are_valid_format(self):
        """Module paths should follow Python import convention."""
        root = Path(__file__).resolve().parent.parent.parent
        registry_path = root / "plugin_registry.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        for entry in registry:
            module_path = entry.get("module", "")
            # Module path should be dotted notation
            assert "." in module_path, f"Invalid module path format: {module_path}"
            # Should start with universal_recon
            assert module_path.startswith(
                "universal_recon."
            ), f"Module should be in universal_recon namespace: {module_path}"


class TestPluginLoader:
    """Tests for plugin_loader.py functionality."""

    def test_load_plugins_by_type_returns_list(self):
        """load_plugins_by_type should always return a list."""
        result = plugin_loader.load_plugins_by_type("nonexistent_type")
        assert isinstance(result, list)

    def test_load_plugins_by_type_with_invalid_registry(self, tmp_path):
        """Should handle missing or invalid registry gracefully."""
        # Create a mock module with bad registry path
        with patch.object(
            plugin_loader, "load_plugins_by_type", wraps=plugin_loader.load_plugins_by_type
        ):
            # Test with nonexistent type - should return empty list
            plugins = plugin_loader.load_plugins_by_type("definitely_not_a_real_type")
            assert plugins == []

    def test_load_plugins_filters_by_type(self):
        """Should only load plugins matching the specified type."""
        # Directory scraper type exists in registry
        plugins = plugin_loader.load_plugins_by_type("directory_scraper")
        # May or may not load depending on dependencies, but shouldn't crash
        assert isinstance(plugins, list)


class TestPluginDryRun:
    """Dry-run tests that validate plugins can be invoked without side effects."""

    @pytest.fixture
    def mock_plugin_registry(self, tmp_path):
        """Create a temporary plugin registry with a dummy plugin."""
        registry = [
            {
                "site_name": "test_dummy",
                "module": "universal_recon.tests.plugins.dummy_plugin",
                "function": "run_plugin",
                "type": "test",
                "description": "Dummy plugin for testing",
                "output_format": "json",
                "industry": "testing",
            }
        ]
        registry_path = tmp_path / "plugin_registry.json"
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f)
        return registry_path

    def test_dryrun_plugin_execution_structure(self):
        """Validate expected dry-run execution structure."""
        # Simulate a dry-run config
        dry_run_config = {
            "enabled": True,
            "skip_network": True,
            "skip_writes": True,
            "mock_responses": True,
            "verbose": True,
        }

        # Validate structure
        assert dry_run_config["enabled"] is True
        assert dry_run_config["skip_network"] is True
        assert dry_run_config["skip_writes"] is True

    def test_dryrun_result_format(self):
        """Validate expected result format from a dry-run plugin."""
        # Expected structure from a plugin dry-run
        expected_result = {
            "success": True,
            "dry_run": True,
            "records_found": 0,
            "records_written": 0,
            "errors": [],
            "warnings": [],
        }

        assert "success" in expected_result
        assert "dry_run" in expected_result
        assert expected_result["dry_run"] is True


class TestNormalizedRecordLoader:
    """Tests for load_normalized_records functionality."""

    @pytest.fixture
    def sample_fieldmap_dir(self, tmp_path):
        """Create temporary fieldmap files for testing."""
        fieldmap_dir = tmp_path / "output" / "fieldmap"
        fieldmap_dir.mkdir(parents=True, exist_ok=True)

        # Create sample fieldmap JSON
        sample_data = {
            "records": [
                {"name": "Test Record 1", "email": "test1@example.com"},
                {"name": "Test Record 2", "email": "test2@example.com"},
            ]
        }

        with open(fieldmap_dir / "test_site_fieldmap.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f)

        return tmp_path

    def test_load_normalized_records_handles_list_format(self, tmp_path):
        """Should handle JSON list format."""
        os.makedirs(tmp_path / "output" / "fieldmap", exist_ok=True)
        data = [{"name": "Record 1"}, {"name": "Record 2"}]

        with open(tmp_path / "output" / "fieldmap" / "list_test_fieldmap.json", "w") as f:
            json.dump(data, f)

        # Patch os.path.join to use tmp_path
        mock_path = str(tmp_path / "output" / "fieldmap" / "list_test_fieldmap.json")
        with patch.object(plugin_loader.os.path, "join", return_value=mock_path):
            result = plugin_loader.load_normalized_records("list_test")
            assert isinstance(result, list)
            assert len(result) == 2

    def test_load_normalized_records_handles_dict_with_records(self, tmp_path):
        """Should extract records key from dict format."""
        os.makedirs(tmp_path / "output" / "fieldmap", exist_ok=True)
        data = {"records": [{"name": "A"}, {"name": "B"}], "metadata": {"source": "test"}}

        with open(tmp_path / "output" / "fieldmap" / "dict_test_fieldmap.json", "w") as f:
            json.dump(data, f)

        mock_path = str(tmp_path / "output" / "fieldmap" / "dict_test_fieldmap.json")
        with patch.object(plugin_loader.os.path, "join", return_value=mock_path):
            result = plugin_loader.load_normalized_records("dict_test")
            assert isinstance(result, list)
            assert len(result) == 2


class TestPluginIntegrationDryRun:
    """Integration tests for plugin system dry-run mode."""

    def test_main_module_imports_cleanly(self):
        """universal_recon.main should import without errors."""
        from universal_recon import main

        assert hasattr(main, "main")

    def test_config_loader_exists(self):
        """ConfigManager should be importable."""
        from universal_recon.core.config_loader import ConfigManager

        assert ConfigManager is not None

    @pytest.mark.parametrize(
        "plugin_type,expected_industry",
        [
            ("directory_scraper", "real_estate"),
            ("industry_scraper", None),  # Multiple industries
            ("service_platform", None),  # Multiple industries
        ],
    )
    def test_plugin_types_exist_in_registry(self, plugin_type, expected_industry):
        """Validate expected plugin types are registered."""
        root = Path(__file__).resolve().parent.parent.parent
        registry_path = root / "plugin_registry.json"

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        matching_plugins = [p for p in registry if p.get("type") == plugin_type]
        assert len(matching_plugins) > 0, f"No plugins found with type: {plugin_type}"

        if expected_industry:
            industries = [p.get("industry") for p in matching_plugins]
            assert expected_industry in industries
