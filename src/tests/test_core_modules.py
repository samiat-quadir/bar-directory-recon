"""
Test suite for core configuration and data processing modules
"""

import json
import os
import tempfile
from typing import Any, Dict

# Import modules to test
from src.config_loader import ConfigLoader, ScrapingConfig
from src.data_extractor import DataExtractor
from src.unified_schema import UnifiedDataRecord


class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_config_loader_init(self) -> None:
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader is not None
        assert hasattr(loader, "config_dir")

    def test_load_config_from_json_file(self) -> None:
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_config = {
                "name": "test-config",
                "description": "Test configuration",
                "base_url": "https://example.com",
                "listing_phase": {},
                "detail_phase": {},
                "pagination": {},
                "data_extraction": {"selectors": {}},  # Add required selectors
                "output": {},
                "options": {},
            }
            json.dump(test_config, f)
            f.flush()

            try:
                loader = ConfigLoader()
                config = loader.load_config(f.name)
                assert isinstance(config, ScrapingConfig)
                assert config.name == "test-config"
                assert config.base_url == "https://example.com"
            finally:
                try:
                    os.unlink(f.name)
                except PermissionError:
                    pass  # File may still be in use on Windows

    def test_config_file_not_found(self) -> None:
        """Test error handling for missing config file."""
        loader = ConfigLoader()
        try:
            loader.load_config("nonexistent.json")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected


class TestDataExtractor:
    """Test cases for DataExtractor class."""

    def test_data_extractor_init(self) -> None:
        """Test DataExtractor initialization."""
        config: Dict[str, Any] = {"extraction_rules": {}}
        extractor = DataExtractor(config)
        assert extractor is not None
        assert hasattr(extractor, "config")
        assert hasattr(extractor, "contact_patterns")

    def test_contact_patterns(self) -> None:
        """Test email and phone pattern matching."""
        config: Dict[str, Any] = {"extraction_rules": {}}
        extractor = DataExtractor(config)

        # Test email pattern
        email_text = "Contact us at info@example.com"
        email_matches = extractor.contact_patterns["email"].findall(email_text)
        assert "info@example.com" in email_matches

        # Test phone pattern
        phone_text = "Call us at (555) 123-4567"
        phone_matches = extractor.contact_patterns["phone"].findall(phone_text)
        assert len(phone_matches) >= 1

    def test_website_pattern(self) -> None:
        """Test website URL pattern matching."""
        config: Dict[str, Any] = {"extraction_rules": {}}
        extractor = DataExtractor(config)

        website_text = "Visit our website at https://example.com"
        website_matches = extractor.contact_patterns["website"].findall(website_text)
        assert len(website_matches) >= 1


class TestUnifiedSchema:
    """Test cases for UnifiedDataRecord class."""

    def test_unified_record_creation(self) -> None:
        """Test creating a unified data record."""
        record = UnifiedDataRecord(
            name="Test Business",
            email="test@business.com",
            phone="555-123-4567",
            address="123 Main St",
            website="https://business.com",
        )

        assert record.name == "Test Business"
        assert record.email == "test@business.com"
        assert record.phone == "555-123-4567"
        assert record.address == "123 Main St"
        assert record.website == "https://business.com"

    def test_unified_record_defaults(self) -> None:
        """Test unified record with default values."""
        record = UnifiedDataRecord()

        assert record.name == ""
        assert record.email == ""
        assert record.phone == ""
        assert record.country == "US"
        assert record.status == "active"
        assert isinstance(record.practice_areas, list)
        assert len(record.practice_areas) == 0

    def test_unified_record_with_lists(self) -> None:
        """Test unified record with list fields."""
        record = UnifiedDataRecord(
            name="Legal Firm",
            practice_areas=["Criminal Law", "Family Law"],
            specializations=["DUI", "Divorce"],
            other_urls=["https://linkedin.com/company/firm"],
        )

        assert record.name == "Legal Firm"
        assert "Criminal Law" in record.practice_areas
        assert "Family Law" in record.practice_areas
        assert "DUI" in record.specializations
        assert "https://linkedin.com/company/firm" in record.other_urls

    def test_unified_record_timestamps(self) -> None:
        """Test unified record timestamp fields."""
        record = UnifiedDataRecord(name="Time Test")

        assert hasattr(record, "scraped_at")
        assert hasattr(record, "last_updated")
        assert record.scraped_at is not None
        assert record.last_updated is not None


class TestIntegrationWorkflows:
    """Integration tests for common workflows."""

    def test_config_to_extractor_workflow(self) -> None:
        """Test configuration to extraction workflow."""
        # Create test config
        config: Dict[str, Any] = {
            "extraction_rules": {
                "listing_container": ".business-listing",
                "fields": {
                    "name": ".business-name",
                    "email": ".contact-email",
                    "phone": ".contact-phone",
                },
            }
        }

        # Create data extractor with config
        extractor = DataExtractor(config)

        # Verify extractor has the config
        assert extractor.config == config
        assert "listing_container" in extractor.extraction_rules

    def test_extraction_to_schema_workflow(self) -> None:
        """Test extraction to unified schema workflow."""
        # Simulate extracted data
        extracted_data = {
            "name": "John's Law Firm",
            "email": "john@lawfirm.com",
            "phone": "555-123-4567",
            "address": "789 Legal Ave",
        }

        # Create unified record from extracted data
        record = UnifiedDataRecord(
            name=extracted_data.get("name", ""),
            email=extracted_data.get("email", ""),
            phone=extracted_data.get("phone", ""),
            address=extracted_data.get("address", ""),
        )

        assert record.name == "John's Law Firm"
        assert record.email == "john@lawfirm.com"
        assert record.phone == "555-123-4567"
        assert record.address == "789 Legal Ave"

    def test_error_handling_workflow(self) -> None:
        """Test error handling in workflows."""
        # Test config loader with invalid file (should raise FileNotFoundError)
        loader = ConfigLoader()
        try:
            loader.load_config("nonexistent.json")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected

        # Test config loader with unsupported format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("invalid config content")
            f.flush()

            try:
                loader.load_config(f.name)
                assert False, "Should raise ValueError for unsupported format"
            except ValueError as e:
                assert "Unsupported config file format" in str(e)
            finally:
                try:
                    os.unlink(f.name)
                except PermissionError:
                    pass

        # Test data extractor with minimal config
        minimal_config: Dict[str, Any] = {}
        extractor = DataExtractor(minimal_config)
        assert extractor.extraction_rules == {}

        # Test unified record with partial data
        partial_record = UnifiedDataRecord(name="Partial Business")
        assert partial_record.name == "Partial Business"
        assert partial_record.email == ""  # Should use default
