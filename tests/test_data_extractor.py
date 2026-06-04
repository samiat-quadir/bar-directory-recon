"""
Tests for data_extractor.py - Data extraction and validation.

Targets:
- DataExtractor initialization
- Contact pattern matching
- Field transformations
- Data cleaning and validation

All tests run without network calls or credentials.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestDataExtractorInit:
    """Tests for DataExtractor initialization."""

    def test_init_with_empty_config(self):
        """DataExtractor should initialize with empty config."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        assert extractor.config == {}
        assert extractor.extraction_rules == {}

    def test_init_with_extraction_rules(self):
        """DataExtractor should store extraction rules."""
        from src.data_extractor import DataExtractor

        config = {
            "extraction_rules": {
                "listing_container": ".directory-item",
                "fields": {"name": {"type": "text", "selectors": [".name"]}},
            }
        }

        extractor = DataExtractor(config)

        assert extractor.extraction_rules["listing_container"] == ".directory-item"


class TestContactPatterns:
    """Tests for contact information extraction patterns."""

    def test_email_pattern_valid(self):
        """Email pattern should match valid emails."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "Contact us at john.doe@example.com for more info"
        match = extractor.contact_patterns["email"].search(text)

        assert match is not None
        assert match.group(0) == "john.doe@example.com"

    def test_email_pattern_multiple(self):
        """Email pattern should find first email in text."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "Primary: alice@test.com, Secondary: bob@test.com"
        match = extractor.contact_patterns["email"].search(text)

        assert match.group(0) == "alice@test.com"

    def test_phone_pattern_standard(self):
        """Phone pattern should match standard formats."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        test_cases = [
            "555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "555 123 4567",
        ]

        for phone in test_cases:
            match = extractor.contact_patterns["phone"].search(f"Call {phone}")
            assert match is not None, f"Failed to match: {phone}"

    def test_phone_pattern_with_country_code(self):
        """Phone pattern should match with country code."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "Call +1-555-123-4567 for support"
        match = extractor.contact_patterns["phone"].search(text)

        assert match is not None

    def test_website_pattern_https(self):
        """Website pattern should match HTTPS URLs."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "Visit https://www.example.com/path for details"
        match = extractor.contact_patterns["website"].search(text)

        assert match is not None
        assert "example.com" in match.group(0)

    def test_website_pattern_www(self):
        """Website pattern should match www URLs."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "Visit www.example.com for more"
        match = extractor.contact_patterns["website"].search(text)

        assert match is not None


class TestExtractContactInfo:
    """Tests for extract_contact_info method."""

    def test_extract_all_contacts(self):
        """extract_contact_info should find all contact types."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = """
        John Doe, Attorney at Law
        Email: john@lawfirm.com
        Phone: (555) 123-4567
        Website: https://www.johnlaw.com
        """

        result = extractor.extract_contact_info(text)

        assert result["email"] == "john@lawfirm.com"
        assert "(555) 123-4567" in result["phone"]
        assert "johnlaw.com" in result["website"]

    def test_extract_contact_info_no_matches(self):
        """extract_contact_info should return empty strings for no matches."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        text = "No contact information here"

        result = extractor.extract_contact_info(text)

        assert result["email"] == ""
        assert result["phone"] == ""
        assert result["website"] == ""


class TestFieldTransformations:
    """Tests for field transformations."""

    def test_transform_strip(self):
        """strip transformation should remove whitespace."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations("  hello  ", ["strip"])

        assert result == "hello"

    def test_transform_lower(self):
        """lower transformation should lowercase text."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations("HELLO World", ["lower"])

        assert result == "hello world"

    def test_transform_upper(self):
        """upper transformation should uppercase text."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations("hello", ["upper"])

        assert result == "HELLO"

    def test_transform_title(self):
        """title transformation should title-case text."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations("john doe", ["title"])

        assert result == "John Doe"

    def test_transform_clean_whitespace(self):
        """clean_whitespace transformation should normalize spaces."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations(
            "hello   world\n\ttest", ["clean_whitespace"]
        )

        assert result == "hello world test"

    def test_transform_replace(self):
        """replace transformation should replace text."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations("hello world", ["replace:world:there"])

        assert result == "hello there"

    def test_transform_regex(self):
        """regex transformation should apply regex replacement."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations(
            "phone: 555-123-4567", ["regex:\\d+-\\d+-\\d+:PHONE"]
        )

        assert result == "phone: PHONE"

    def test_transform_multiple(self):
        """Multiple transformations should apply in order."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._apply_transformations(
            "  HELLO WORLD  ", ["strip", "lower", "title"]
        )

        assert result == "Hello World"


class TestRecordValidation:
    """Tests for record validation."""

    def test_is_valid_record_with_name(self):
        """Record with name should be valid."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._is_valid_record({"name": "John Doe"})

        assert result is True

    def test_is_valid_record_with_email(self):
        """Record with email should be valid."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._is_valid_record({"email": "john@example.com"})

        assert result is True

    def test_is_valid_record_with_phone(self):
        """Record with phone should be valid."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._is_valid_record({"phone": "555-123-4567"})

        assert result is True

    def test_is_valid_record_empty(self):
        """Empty record should be invalid."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        result = extractor._is_valid_record({})

        assert result is False

    def test_is_valid_record_with_required_fields(self):
        """Record should validate against required_fields config."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({"required_fields": ["name", "email"]})

        valid = extractor._is_valid_record(
            {"name": "John", "email": "john@example.com"}
        )
        invalid = extractor._is_valid_record({"name": "John"})

        assert valid is True
        assert invalid is False


class TestDataCleaning:
    """Tests for data cleaning."""

    def test_clean_extracted_data_removes_duplicates(self):
        """clean_extracted_data should remove duplicates."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "John Doe", "email": "john@example.com"},  # Duplicate
            {"name": "Jane Smith", "email": "jane@example.com"},
        ]

        cleaned = extractor.clean_extracted_data(data)

        assert len(cleaned) == 2

    def test_clean_extracted_data_normalizes_whitespace(self):
        """clean_extracted_data should normalize whitespace."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "  John   Doe  ", "email": "john@example.com"}]

        cleaned = extractor.clean_extracted_data(data)

        assert cleaned[0]["name"] == "John Doe"


class TestDataEnrichment:
    """Tests for data enrichment and validation."""

    def test_validate_and_enrich_invalid_email(self):
        """validate_and_enrich_data should clear invalid emails."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "email": "not-an-email"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["email"] == ""

    def test_validate_and_enrich_valid_email(self):
        """validate_and_enrich_data should keep valid emails."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "email": "john@example.com"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["email"] == "john@example.com"

    def test_validate_and_enrich_phone_format(self):
        """validate_and_enrich_data should format phone numbers."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "phone": "5551234567"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["phone"] == "(555) 123-4567"

    def test_validate_and_enrich_phone_with_country_code(self):
        """validate_and_enrich_data should handle phone with country code."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "phone": "15551234567"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["phone"] == "(555) 123-4567"

    def test_validate_and_enrich_invalid_phone(self):
        """validate_and_enrich_data should clear invalid phones."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "phone": "123"}]  # Too short

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["phone"] == ""

    def test_validate_and_enrich_website(self):
        """validate_and_enrich_data should add protocol to websites."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        data = [{"name": "John", "website": "www.example.com"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["website"] == "https://www.example.com"

    def test_validate_and_enrich_adds_source(self):
        """validate_and_enrich_data should add source info."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({"source_name": "TestDirectory"})

        data = [{"name": "John"}]

        enriched = extractor.validate_and_enrich_data(data)

        assert enriched[0]["source"] == "TestDirectory"


class TestTimestamp:
    """Tests for timestamp handling."""

    def test_get_timestamp_format(self):
        """_get_timestamp should return ISO format string."""
        from src.data_extractor import DataExtractor

        extractor = DataExtractor({})

        timestamp = extractor._get_timestamp()

        # Should be parseable ISO format
        from datetime import datetime
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None
