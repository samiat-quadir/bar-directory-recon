#!/usr/bin/env python3
"""
Tests for the ConfigLoader module.
"""

import os
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import patch

from src.config_loader import ConfigLoader, ScrapingConfig


class TestConfigLoader(unittest.TestCase):
    """Test cases for the ConfigLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.config_loader = ConfigLoader(config_dir=self.config_dir)

        # Sample valid config for testing
        self.sample_config_dict = {
            "name": "Test Directory",
            "description": "Test scraping configuration",
            "base_url": "https://test-directory.com",
            "listing_phase": {
                "enabled": True,
                "start_url": "https://test-directory.com/list",
                "list_selector": ".directory-item",
            },
            "detail_phase": {"enabled": True, "delay": 1.0},
            "pagination": {"enabled": True, "type": "next_button"},
            "data_extraction": {
                "selectors": {"name": {"css": ["h1", ".name"], "required": True}}
            },
            "output": {"format": "csv", "filename": "test_directory.csv"},
            "options": {"headless": True},
        }

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test initialization with config directory."""
        self.assertEqual(self.config_loader.config_dir, self.config_dir)

        # Test with default config directory
        with patch.object(Path, "mkdir") as mock_mkdir:
            loader = ConfigLoader()
            self.assertEqual(loader.config_dir, Path("config"))
            mock_mkdir.assert_called_once()

    def test_load_config_json(self):
        """Test loading a JSON configuration file."""
        # Create a temporary JSON config file
        with NamedTemporaryFile(
            suffix=".json", dir=self.config_dir, delete=False
        ) as temp_file:
            import json

            json.dump(self.sample_config_dict, temp_file)
            temp_file_path = temp_file.name

        # Load the config
        config = self.config_loader.load_config(temp_file_path)

        # Verify the config was loaded correctly
        self.assertIsInstance(config, ScrapingConfig)
        self.assertEqual(config.name, "Test Directory")
        self.assertEqual(config.base_url, "https://test-directory.com")
        self.assertTrue(config.listing_phase["enabled"])
        self.assertEqual(config.pagination["type"], "next_button")

        # Clean up
        os.unlink(temp_file_path)

    def test_load_config_yaml(self):
        """Test loading a YAML configuration file."""
        # Create a temporary YAML config file
        with NamedTemporaryFile(
            suffix=".yaml", dir=self.config_dir, delete=False
        ) as temp_file:
            import yaml

            yaml.dump(self.sample_config_dict, temp_file)
            temp_file_path = temp_file.name

        # Load the config
        config = self.config_loader.load_config(temp_file_path)

        # Verify the config was loaded correctly
        self.assertIsInstance(config, ScrapingConfig)
        self.assertEqual(config.name, "Test Directory")
        self.assertEqual(config.base_url, "https://test-directory.com")

        # Clean up
        os.unlink(temp_file_path)

    def test_load_config_file_not_found(self):
        """Test loading a non-existent configuration file."""
        with self.assertRaises(FileNotFoundError):
            self.config_loader.load_config("nonexistent_config.json")

    def test_load_config_unsupported_format(self):
        """Test loading a configuration file with unsupported format."""
        # Create a temporary file with unsupported extension
        with NamedTemporaryFile(
            suffix=".txt", dir=self.config_dir, delete=False
        ) as temp_file:
            temp_file.write(b"Not a valid config")
            temp_file_path = temp_file.name

        with self.assertRaises(ValueError):
            self.config_loader.load_config(temp_file_path)

        # Clean up
        os.unlink(temp_file_path)

    def test_save_config_json(self):
        """Test saving a configuration to a JSON file."""
        # Create a config object
        config = ScrapingConfig(**self.sample_config_dict)

        # Save to a temporary JSON file
        output_path = Path(self.config_dir) / "test_config_output.json"
        self.config_loader.save_config(config, output_path)

        # Verify the file was created
        self.assertTrue(output_path.exists())

        # Load the saved config and verify contents
        with open(output_path, "r") as f:
            import json

            saved_data = json.load(f)

        self.assertEqual(saved_data["name"], "Test Directory")
        self.assertEqual(saved_data["base_url"], "https://test-directory.com")

    def test_save_config_yaml(self):
        """Test saving a configuration to a YAML file."""
        # Create a config object
        config = ScrapingConfig(**self.sample_config_dict)

        # Save to a temporary YAML file
        output_path = Path(self.config_dir) / "test_config_output.yaml"
        self.config_loader.save_config(config, output_path)

        # Verify the file was created
        self.assertTrue(output_path.exists())

        # Load the saved config and verify contents
        with open(output_path, "r") as f:
            import yaml

            saved_data = yaml.safe_load(f)

        self.assertEqual(saved_data["name"], "Test Directory")
        self.assertEqual(saved_data["base_url"], "https://test-directory.com")

    def test_save_config_unsupported_format(self):
        """Test saving a configuration to an unsupported format."""
        # Create a config object
        config = ScrapingConfig(**self.sample_config_dict)

        # Attempt to save to an unsupported format
        with self.assertRaises(ValueError):
            self.config_loader.save_config(config, "config.txt")

    def test_list_configs(self):
        """Test listing available configuration files."""
        # Create a few configuration files
        test_files = [
            ("config1.json", "json"),
            ("config2.yaml", "yaml"),
            ("config3.yml", "yaml"),
            ("not_a_config.txt", "text"),  # Should be ignored
        ]

        for filename, file_type in test_files:
            path = Path(self.config_dir) / filename
            with open(path, "w") as f:
                if file_type == "json":
                    import json

                    json.dump({"test": "data"}, f)
                elif file_type == "yaml":
                    import yaml

                    yaml.dump({"test": "data"}, f)
                else:
                    f.write("Not a config file")

        # Get list of configs
        configs = self.config_loader.list_configs()

        # Should find 3 config files (ignoring .txt)
        self.assertEqual(len(configs), 3)
        self.assertIn("config1", configs)
        self.assertIn("config2", configs)
        self.assertIn("config3", configs)
        self.assertNotIn("not_a_config", configs)

    def test_generate_sample_config(self):
        """Test generating a sample configuration."""
        # Generate sample config
        config = self.config_loader.generate_sample_config(
            "Sample Directory", "https://example.com"
        )

        # Verify the sample config has expected structure
        self.assertEqual(config.name, "Sample Directory")
        self.assertEqual(config.base_url, "https://example.com")
        self.assertTrue(isinstance(config.listing_phase, dict))
        self.assertTrue(isinstance(config.pagination, dict))
        self.assertTrue(isinstance(config.data_extraction, dict))
        self.assertTrue(isinstance(config.output, dict))
        self.assertTrue(isinstance(config.options, dict))

    def test_validate_config(self):
        """Test configuration validation."""
        # Create a valid config
        valid_config = ScrapingConfig(**self.sample_config_dict)

        # Validate and check results
        validation = self.config_loader.validate_config(valid_config)
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["errors"]), 0)

        # Create an invalid config (missing base_url)
        invalid_config_dict = self.sample_config_dict.copy()
        invalid_config_dict["base_url"] = ""
        invalid_config = ScrapingConfig(**invalid_config_dict)

        # Validate and check results
        validation = self.config_loader.validate_config(invalid_config)
        self.assertFalse(validation["valid"])
        self.assertGreater(len(validation["errors"]), 0)

        # Check specific error
        self.assertIn("Base URL is required", validation["errors"])

    def test_validate_selectors(self):
        """Test validation of CSS selectors."""
        # Valid selectors
        valid_selectors = {
            "name": {"css": ["h1", ".name"]},
            "email": {"css": ["a[href^='mailto:']"]},
        }

        issues = self.config_loader.validate_selectors(valid_selectors)
        self.assertEqual(len(issues), 0)

        # Invalid selectors (missing css or xpath)
        invalid_selectors = {"name": {"required": True}}  # Missing css or xpath

        issues = self.config_loader.validate_selectors(invalid_selectors)
        self.assertEqual(len(issues), 1)

    def test_get_selector_priority(self):
        """Test getting CSS selectors in priority order."""
        selector_config = {"css": ["h1", ".name", ".title"]}

        selectors = self.config_loader.get_selector_priority(selector_config)
        self.assertEqual(selectors, ["h1", ".name", ".title"])

        # Test with string instead of list
        selector_config = {"css": "h1"}

        selectors = self.config_loader.get_selector_priority(selector_config)
        self.assertEqual(selectors, ["h1"])

        # Test with empty config
        selector_config = {}

        selectors = self.config_loader.get_selector_priority(selector_config)
        self.assertEqual(selectors, [])

    def test_is_required_field(self):
        """Test checking if a field is required."""
        # Create config with required fields
        config_dict = self.sample_config_dict.copy()
        config_dict["data_extraction"]["selectors"] = {
            "name": {"css": ["h1"], "required": True},
            "email": {"css": ["a"], "required": False},
        }

        config = ScrapingConfig(**config_dict)

        # Check required fields
        self.assertTrue(self.config_loader.is_required_field("name", config))
        self.assertFalse(self.config_loader.is_required_field("email", config))
        self.assertFalse(self.config_loader.is_required_field("nonexistent", config))

    def test_get_extraction_patterns(self):
        """Test getting regex patterns for field extraction."""
        # Create config with extraction patterns
        config_dict = self.sample_config_dict.copy()
        config_dict["data_extraction"]["selectors"] = {
            "phone": {
                "css": [".phone"],
                "patterns": [r"\d{3}-\d{3}-\d{4}", r"\(\d{3}\) \d{3}-\d{4}"],
            },
            "email": {
                "css": [".email"],
                "patterns": r"[a-z0-9]+@[a-z0-9]+",  # Single pattern as string
            },
            "name": {"css": [".name"]},  # No patterns
        }

        config = ScrapingConfig(**config_dict)

        # Check patterns
        phone_patterns = self.config_loader.get_extraction_patterns("phone", config)
        self.assertEqual(
            phone_patterns, [r"\d{3}-\d{3}-\d{4}", r"\(\d{3}\) \d{3}-\d{4}"]
        )

        email_patterns = self.config_loader.get_extraction_patterns("email", config)
        self.assertEqual(email_patterns, [r"[a-z0-9]+@[a-z0-9]+"])

        name_patterns = self.config_loader.get_extraction_patterns("name", config)
        self.assertEqual(name_patterns, [])


if __name__ == "__main__":
    unittest.main()
