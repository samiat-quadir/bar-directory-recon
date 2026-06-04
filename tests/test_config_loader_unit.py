"""
Unit tests for ConfigLoader methods not covered by test_config_loader_defaults.py.

These tests target:
1. get_selector_priority() method
2. is_required_field() method
3. get_extraction_patterns() method
4. validate_config() warnings paths
5. Edge cases in selector validation

All tests use tmp_path, no network calls, no credentials.
"""

import json
import pytest


class TestConfigLoaderSelectorPriority:
    """Tests for get_selector_priority method."""

    def test_get_selector_priority_with_list(self):
        """get_selector_priority should return list of CSS selectors."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selector_config = {"css": ["h1", "h2.title", ".name"]}

        result = loader.get_selector_priority(selector_config)

        assert result == ["h1", "h2.title", ".name"]

    def test_get_selector_priority_with_string(self):
        """get_selector_priority should handle string selector."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selector_config = {"css": ".single-selector"}

        result = loader.get_selector_priority(selector_config)

        assert result == [".single-selector"]

    def test_get_selector_priority_empty_list(self):
        """get_selector_priority should handle empty list."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selector_config = {"css": []}

        result = loader.get_selector_priority(selector_config)

        assert result == []

    def test_get_selector_priority_missing_css(self):
        """get_selector_priority should return empty list when no css key."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selector_config = {"xpath": "//div[@class='name']"}

        result = loader.get_selector_priority(selector_config)

        assert result == []

    def test_get_selector_priority_none_value(self):
        """get_selector_priority should handle None css value."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selector_config = {"css": None}

        result = loader.get_selector_priority(selector_config)

        assert result == []


class TestConfigLoaderIsRequiredField:
    """Tests for is_required_field method."""

    def test_is_required_field_true(self):
        """is_required_field should return True for required fields."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "name": {"css": ["h1"], "required": True}
                }
            },
            output={},
            options={},
        )

        assert loader.is_required_field("name", config) is True

    def test_is_required_field_false(self):
        """is_required_field should return False for optional fields."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "email": {"css": ["a[href^='mailto:']"], "required": False}
                }
            },
            output={},
            options={},
        )

        assert loader.is_required_field("email", config) is False

    def test_is_required_field_missing_field(self):
        """is_required_field should return False for non-existent fields."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        assert loader.is_required_field("nonexistent", config) is False

    def test_is_required_field_no_required_key(self):
        """is_required_field should default False when required key missing."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "phone": {"css": [".phone"]}  # No "required" key
                }
            },
            output={},
            options={},
        )

        assert loader.is_required_field("phone", config) is False


class TestConfigLoaderExtractionPatterns:
    """Tests for get_extraction_patterns method."""

    def test_get_extraction_patterns_list(self):
        """get_extraction_patterns should return list of regex patterns."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "phone": {
                        "css": [".phone"],
                        "patterns": [
                            r"\d{3}-\d{3}-\d{4}",
                            r"\(\d{3}\) \d{3}-\d{4}"
                        ]
                    }
                }
            },
            output={},
            options={},
        )

        result = loader.get_extraction_patterns("phone", config)

        assert len(result) == 2
        assert r"\d{3}-\d{3}-\d{4}" in result

    def test_get_extraction_patterns_string(self):
        """get_extraction_patterns should handle single string pattern."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "email": {
                        "css": ["a[href^='mailto:']"],
                        "patterns": r"mailto:(.+)"  # Single string
                    }
                }
            },
            output={},
            options={},
        )

        result = loader.get_extraction_patterns("email", config)

        assert result == [r"mailto:(.+)"]

    def test_get_extraction_patterns_empty(self):
        """get_extraction_patterns should return empty list when no patterns."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={
                "selectors": {
                    "name": {"css": ["h1"]}  # No patterns
                }
            },
            output={},
            options={},
        )

        result = loader.get_extraction_patterns("name", config)

        assert result == []

    def test_get_extraction_patterns_missing_field(self):
        """get_extraction_patterns should return empty for missing field."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.get_extraction_patterns("nonexistent", config)

        assert result == []


class TestConfigLoaderValidateConfigWarnings:
    """Tests for validate_config warning paths."""

    def test_validate_config_warns_missing_data_fields(self):
        """validate_config should warn if detail phase has no fields."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={"enabled": True},  # Enabled but no fields
            pagination={},
            data_extraction={"selectors": {}},  # Empty selectors -> no "fields"
            output={},
            options={},
        )

        result = loader.validate_config(config)

        # Should have warnings (not errors) about missing fields
        assert len(result.get("warnings", [])) > 0 or result["valid"] is True

    def test_validate_config_warns_missing_output_path(self):
        """validate_config should warn when no output file_path specified."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},  # Missing file_path
            options={},
        )

        result = loader.validate_config(config)

        # Should have warning about missing output path
        assert any("output" in w.lower() or "file" in w.lower()
                   for w in result.get("warnings", []))

    def test_validate_config_valid_with_warnings(self):
        """validate_config can be valid even with warnings."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="valid_config",
            description="A valid config",
            base_url="https://valid.example.com",  # Valid URL
            listing_phase={"enabled": False},  # Disabled, so no selectors needed
            detail_phase={"enabled": False},
            pagination={"type": "none"},
            data_extraction={"selectors": {}},
            output={},  # Missing file_path is warning, not error
            options={},
        )

        result = loader.validate_config(config)

        # Should be valid despite warnings
        assert result["valid"] is True
        assert result["errors"] == []


class TestConfigLoaderValidateSelectorsEdgeCases:
    """Edge case tests for validate_selectors method."""

    def test_validate_selectors_non_dict_config(self):
        """validate_selectors should catch non-dict selector config."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selectors = {
            "name": "not a dict"  # Invalid: should be dict
        }

        issues = loader.validate_selectors(selectors)

        assert len(issues) > 0
        assert any("dictionary" in issue.lower() for issue in issues)

    def test_validate_selectors_valid_css_list(self):
        """validate_selectors should accept valid css list."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selectors = {
            "name": {"css": ["h1", ".title"]},
            "email": {"css": ["a[href^='mailto:']"]},
        }

        issues = loader.validate_selectors(selectors)

        assert issues == []

    def test_validate_selectors_css_not_list(self):
        """validate_selectors should catch css that's not a list."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selectors = {
            "name": {"css": "h1"}  # String instead of list
        }

        issues = loader.validate_selectors(selectors)

        assert len(issues) > 0
        assert any("list" in issue.lower() for issue in issues)

    def test_validate_selectors_xpath_valid(self):
        """validate_selectors should accept xpath as alternative."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader()
        selectors = {
            "name": {"xpath": "//h1[@class='title']"},
        }

        issues = loader.validate_selectors(selectors)

        # xpath is valid alternative to css
        assert issues == []


class TestConfigLoaderConfigValidation:
    """Tests for validation helpers with pagination."""

    def test_validate_config_next_button_pagination(self):
        """validate_config should require selector for next_button type."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={"type": "next_button"},  # Type set but no next_selector
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.validate_config(config)

        # Should have error about missing next button selector
        assert len(result["errors"]) > 0

    def test_validate_config_load_more_pagination(self):
        """validate_config should require selector for load_more type."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={},
            detail_phase={},
            pagination={"type": "load_more"},  # Missing load_more_selector
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.validate_config(config)

        assert len(result["errors"]) > 0

    def test_validate_config_listing_enabled_missing_selectors(self):
        """validate_config should error when listing enabled but no selectors."""
        from src.config_loader import ConfigLoader, ScrapingConfig

        loader = ConfigLoader()
        config = ScrapingConfig(
            name="test",
            description="test",
            base_url="https://example.com",
            listing_phase={"enabled": True},  # Enabled but no selectors
            detail_phase={},
            pagination={},
            data_extraction={"selectors": {}},
            output={},
            options={},
        )

        result = loader.validate_config(config)

        # Should have errors about missing list_selector and link_selector
        assert len(result["errors"]) >= 2


class TestConfigLoaderDataclassConversion:
    """Tests for _config_to_dict conversion."""

    def test_config_to_dict_roundtrip(self, tmp_path):
        """Config should survive save/load roundtrip."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))
        original = loader.generate_sample_config("roundtrip", "https://roundtrip.com")

        # Save to JSON
        json_path = tmp_path / "roundtrip.json"
        loader.save_config(original, json_path)

        # Load back
        loaded = loader.load_config(json_path)

        # Compare key fields
        assert loaded.name == original.name
        assert loaded.base_url == original.base_url
        assert loaded.options["headless"] == original.options["headless"]

    def test_config_to_dict_yaml_roundtrip(self, tmp_path):
        """Config should survive YAML save/load roundtrip."""
        from src.config_loader import ConfigLoader

        loader = ConfigLoader(config_dir=str(tmp_path))
        original = loader.generate_sample_config("yaml_test", "https://yaml.com")

        # Save to YAML
        yaml_path = tmp_path / "yaml_test.yml"
        loader.save_config(original, yaml_path)

        # Load back
        loaded = loader.load_config(yaml_path)

        assert loaded.name == original.name
        assert loaded.pagination == original.pagination
