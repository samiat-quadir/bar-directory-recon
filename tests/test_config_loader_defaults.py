"""
Tests for configuration loader defaults and error paths.

These tests verify:
1. ConfigLoader handles missing files gracefully
2. Default values are applied correctly
3. Invalid config formats raise appropriate errors
4. Config validation catches common mistakes
"""

import json

import pytest
import yaml


class TestConfigLoaderDefaults:
    """Tests for ConfigLoader default behavior."""

    def test_config_loader_creates_config_dir(self, tmp_path):
        """ConfigLoader should create config dir if missing."""
        from src.config_loader import ConfigLoader

        config_dir = tmp_path / "new_config_dir"
        ConfigLoader(config_dir=str(config_dir))

        assert config_dir.exists()

    def test_config_loader_lists_empty_dir(self, tmp_path):
        """list_configs should return empty list for empty dir."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))
        configs = loader.list_configs()

        assert configs == []

    def test_config_loader_lists_json_and_yaml(self, tmp_path):
        """list_configs should find both JSON and YAML files."""
        from src.config_loader import ConfigLoader

        # Create test config files
        (tmp_path / "config1.json").write_text("{}")
        (tmp_path / "config2.yaml").write_text("")
        (tmp_path / "config3.yml").write_text("")

        loader = ConfigLoader(config_dir=str(tmp_path))
        configs = loader.list_configs()

        assert "config1" in configs
        assert "config2" in configs
        assert "config3" in configs


class TestConfigLoaderErrorPaths:
    """Tests for ConfigLoader error handling."""

    def test_load_config_file_not_found(self, tmp_path):
        """load_config should raise FileNotFoundError for missing files."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            loader.load_config(tmp_path / "nonexistent.json")

    def test_load_config_unsupported_format(self, tmp_path):
        """load_config should raise ValueError for unsupported formats."""
        from src.config_loader import ConfigLoader

        # Create file with unsupported extension
        bad_file = tmp_path / "config.txt"
        bad_file.write_text("some content")

        loader = ConfigLoader(config_dir=str(tmp_path))

        with pytest.raises(ValueError) as exc_info:
            loader.load_config(bad_file)

        assert "Unsupported" in str(exc_info.value)

    def test_load_config_missing_required_field(self, tmp_path):
        """load_config should raise ValueError for missing required fields."""
        from src.config_loader import ConfigLoader

        # Create config missing required fields
        bad_config = tmp_path / "bad.json"
        bad_config.write_text(json.dumps({"name": "test"}))

        loader = ConfigLoader(config_dir=str(tmp_path))

        with pytest.raises(ValueError) as exc_info:
            loader.load_config(bad_config)

        assert "Missing required field" in str(exc_info.value)

    def test_load_config_invalid_listing_phase(self, tmp_path):
        """load_config should validate listing_phase is dict."""
        from src.config_loader import ConfigLoader

        bad_config = tmp_path / "bad.json"
        bad_config.write_text(json.dumps({
            "name": "test",
            "description": "test desc",
            "base_url": "https://example.com",
            "listing_phase": "not a dict",  # Invalid
            "detail_phase": {},
            "pagination": {},
            "data_extraction": {"selectors": {}},
            "output": {},
            "options": {},
        }))

        loader = ConfigLoader(config_dir=str(tmp_path))

        with pytest.raises(ValueError) as exc_info:
            loader.load_config(bad_config)

        assert "listing_phase" in str(exc_info.value)


class TestConfigLoaderLoadFormats:
    """Tests for loading different config formats."""

    def test_load_json_config(self, tmp_path):
        """ConfigLoader should load JSON configs correctly."""
        from src.config_loader import ConfigLoader

        config_data = {
            "name": "test_scraper",
            "description": "Test description",
            "base_url": "https://example.com",
            "listing_phase": {"enabled": True},
            "detail_phase": {"enabled": True},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True},
        }

        config_file = tmp_path / "test.json"
        config_file.write_text(json.dumps(config_data))

        loader = ConfigLoader(config_dir=str(tmp_path))
        config = loader.load_config(config_file)

        assert config.name == "test_scraper"
        assert config.base_url == "https://example.com"

    def test_load_yaml_config(self, tmp_path):
        """ConfigLoader should load YAML configs correctly."""
        from src.config_loader import ConfigLoader

        config_data = {
            "name": "yaml_scraper",
            "description": "YAML test",
            "base_url": "https://yaml-example.com",
            "listing_phase": {"enabled": True},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": True, "type": "auto"},
            "data_extraction": {"selectors": {"name": {"css": ["h1"]}}},
            "output": {"format": "json"},
            "options": {"timeout": 30},
        }

        config_file = tmp_path / "test.yaml"
        config_file.write_text(yaml.dump(config_data))

        loader = ConfigLoader(config_dir=str(tmp_path))
        config = loader.load_config(config_file)

        assert config.name == "yaml_scraper"
        assert config.pagination["type"] == "auto"


class TestConfigLoaderSaveConfig:
    """Tests for saving configurations."""

    def test_save_config_json(self, tmp_path):
        """ConfigLoader should save JSON configs correctly."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))
        sample = loader.generate_sample_config("save_test", "https://save.com")

        output_file = tmp_path / "saved.json"
        loader.save_config(sample, output_file)

        assert output_file.exists()

        # Verify saved content
        saved_data = json.loads(output_file.read_text())
        assert saved_data["name"] == "save_test"

    def test_save_config_yaml(self, tmp_path):
        """ConfigLoader should save YAML configs correctly."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))
        sample = loader.generate_sample_config("yaml_save", "https://yaml.com")

        output_file = tmp_path / "saved.yaml"
        loader.save_config(sample, output_file)

        assert output_file.exists()

        # Verify saved content
        saved_data = yaml.safe_load(output_file.read_text())
        assert saved_data["name"] == "yaml_save"


class TestConfigLoaderGenerateSample:
    """Tests for sample configuration generation."""

    def test_generate_sample_config_has_defaults(self):
        """generate_sample_config should provide sensible defaults."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        sample = loader.generate_sample_config("test_dir", "https://test.com")

        # Check defaults are set
        assert sample.listing_phase["enabled"] is True
        assert sample.listing_phase["max_pages"] == 10
        assert sample.options["headless"] is True
        assert sample.options["timeout"] == 30

    def test_generate_sample_config_filename_format(self):
        """generate_sample_config should format filename correctly."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        sample = loader.generate_sample_config("State Bar Directory", "https://bar.org")

        expected_filename = "state_bar_directory_directory.csv"
        assert sample.output["filename"] == expected_filename


class TestConfigLoaderValidation:
    """Tests for configuration validation."""

    def test_validate_config_catches_missing_url(self):
        """validate_config should catch missing base_url."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="",  # Missing URL
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.validate_config(config)

        assert result["valid"] is False
        assert any("Base URL" in err for err in result["errors"])

    def test_validate_config_catches_invalid_url_scheme(self):
        """validate_config should catch URLs without http(s)."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="ftp://invalid.com",  # Not http/https
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.validate_config(config)

        assert result["valid"] is False
        assert any("http" in err.lower() for err in result["errors"])

    def test_validate_selectors_catches_missing_css(self):
        """validate_selectors should catch selectors without css/xpath."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selectors = {
            "name": {"required": True},  # Missing css or xpath
        }

        issues = loader.validate_selectors(selectors)

        assert len(issues) > 0
        assert any("css" in issue.lower() or "xpath" in issue.lower() for issue in issues)


class TestUniversalReconConfigManager:
    """Tests for universal_recon ConfigManager."""

    def test_config_manager_missing_file(self, tmp_path):
        """ConfigManager should handle missing config file gracefully."""
        from universal_recon.core.config_loader import ConfigManager

        manager = ConfigManager(config_path=str(tmp_path / "nonexistent.json"))

        # Should not raise, just have empty config
        assert manager.config == {}

    def test_config_manager_as_dict(self, tmp_path):
        """ConfigManager.as_dict should return config dictionary."""
        from universal_recon.core.config_loader import ConfigManager

        config_data = {"site1": {"url": "https://site1.com"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        manager = ConfigManager(config_path=str(config_file))

        assert manager.as_dict() == config_data

    def test_config_manager_get_site_config(self, tmp_path):
        """ConfigManager.get_site_config should return site-specific config."""
        from universal_recon.core.config_loader import ConfigManager

        config_data = {
            "site1": {"url": "https://site1.com", "delay": 2},
            "site2": {"url": "https://site2.com", "delay": 3},
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        manager = ConfigManager(config_path=str(config_file))

        site1_config = manager.get_site_config("site1")
        assert site1_config["delay"] == 2

        # Missing site should return empty dict
        missing = manager.get_site_config("nonexistent")
        assert missing == {}
