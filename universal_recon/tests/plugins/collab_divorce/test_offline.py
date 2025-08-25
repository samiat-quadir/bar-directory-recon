"""Offline tests for collaborative divorce plugin.

These tests run without network connectivity and use mock data
to validate the plugin's data processing and transformation logic.
"""

import pytest
from unittest.mock import patch, MagicMock

from universal_recon.plugins.collab_divorce import CollabDivorcePlugin


class TestCollabDivorcePluginOffline:
    """Test suite for offline collaborative divorce plugin functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = CollabDivorcePlugin()

    def test_plugin_name(self):
        """Test plugin name property."""
        assert self.plugin.name == "collab_divorce"

    def test_fetch_mock_data(self):
        """Test fetch method returns mock attorney data."""
        records = list(self.plugin.fetch())
        
        assert len(records) == 2
        assert all("name" in record for record in records)
        assert all("email" in record for record in records)
        assert any("Sarah Johnson" in record["name"] for record in records)
        assert any("Michael Chen" in record["name"] for record in records)

    def test_transform_attorney_data(self):
        """Test data transformation for attorney records."""
        raw_data = {
            "name": "Dr. Sarah Johnson, JD",
            "practice_areas": ["Collaborative Divorce", "Family Mediation"],
            "location": "San Francisco, CA",
            "phone": "(415) 555-0123",
            "email": "sarah.johnson@collablaw.com",
            "certifications": ["Collaborative Process Certified"],
            "years_experience": 15,
            "collaborative_cases": 150,
            "raw_url": "https://collaborativedivorce.org/attorneys/sarah-johnson"
        }
        
        transformed = self.plugin.transform(raw_data)
        
        assert transformed["name"] == "Dr. Sarah Johnson, JD"
        assert transformed["email"] == "sarah.johnson@collablaw.com"
        assert transformed["phone"] == "(415) 555-0123"
        assert transformed["city"] == "San Francisco"
        assert transformed["state"] == "CA"
        assert transformed["years_experience"] == 15
        assert transformed["collaborative_cases"] == 150
        assert transformed["plugin_name"] == "collab_divorce"
        assert transformed["record_type"] == "collaborative_attorney"
        assert transformed["firm_domain"] == "collablaw.com"

    def test_validate_valid_data(self):
        """Test validation with valid attorney data."""
        valid_data = {
            "name": "John Doe, Esq.",
            "email": "john.doe@legalfirm.com",
            "phone": "(555) 123-4567",
            "city": "Seattle",
            "state": "WA",
            "practice_areas": ["Collaborative Law"],
            "years_experience": 10
        }
        
        assert self.plugin.validate(valid_data) is True

    def test_validate_invalid_email(self):
        """Test validation fails with invalid email."""
        invalid_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "phone": "(555) 123-4567",
            "city": "Seattle",
            "state": "WA"
        }
        
        assert self.plugin.validate(invalid_data) is False

    def test_validate_missing_required_field(self):
        """Test validation fails with missing required fields."""
        incomplete_data = {
            "name": "John Doe",
            "email": "john@example.com",
            # Missing phone, city, state
        }
        
        assert self.plugin.validate(incomplete_data) is False

    def test_validate_invalid_state_code(self):
        """Test validation fails with invalid state code."""
        invalid_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "city": "Seattle",
            "state": "INVALID"  # Should be 2-letter code
        }
        
        assert self.plugin.validate(invalid_data) is False

    def test_parse_location_city_state(self):
        """Test location parsing for city, state format."""
        city, state = self.plugin._parse_location("San Francisco, CA")
        assert city == "San Francisco"
        assert state == "CA"

    def test_parse_location_full_state_name(self):
        """Test location parsing with full state name."""
        city, state = self.plugin._parse_location("Portland, Oregon OR")
        assert city == "Portland"
        assert state == "OR"

    def test_parse_location_empty(self):
        """Test location parsing with empty input."""
        city, state = self.plugin._parse_location("")
        assert city == ""
        assert state == ""

    def test_normalize_phone_standard_format(self):
        """Test phone normalization for standard 10-digit number."""
        normalized = self.plugin._normalize_phone("4155550123")
        assert normalized == "(415) 555-0123"

    def test_normalize_phone_with_country_code(self):
        """Test phone normalization with country code."""
        normalized = self.plugin._normalize_phone("14155550123")
        assert normalized == "(415) 555-0123"

    def test_normalize_phone_formatted_input(self):
        """Test phone normalization with already formatted input."""
        normalized = self.plugin._normalize_phone("(415) 555-0123")
        assert normalized == "(415) 555-0123"

    def test_extract_domain_valid_email(self):
        """Test domain extraction from valid email."""
        domain = self.plugin._extract_domain("user@example.com")
        assert domain == "example.com"

    def test_extract_domain_invalid_email(self):
        """Test domain extraction from invalid email."""
        domain = self.plugin._extract_domain("invalid-email")
        assert domain == ""

    def test_calculate_experience_score(self):
        """Test experience score calculation."""
        score = self.plugin._calculate_experience_score(15, 150)
        assert score == 100.0  # (15*2) + min(150*0.5, 70) = 30 + 70 = 100

    def test_calculate_experience_score_max_caps(self):
        """Test experience score calculation with maximum caps."""
        score = self.plugin._calculate_experience_score(25, 200)
        assert score == 100.0  # Max 30 for years + Max 70 for cases = 100

    def test_is_valid_email_valid_cases(self):
        """Test email validation with valid cases."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "attorney+law@firm.co.uk"
        ]
        
        for email in valid_emails:
            assert self.plugin._is_valid_email(email) is True

    def test_is_valid_email_invalid_cases(self):
        """Test email validation with invalid cases."""
        invalid_emails = [
            "",
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain"
        ]
        
        for email in invalid_emails:
            assert self.plugin._is_valid_email(email) is False

    def test_is_valid_phone_valid_formats(self):
        """Test phone validation with valid formats."""
        valid_phones = [
            "(415) 555-0123",
            "415-555-0123",
            "4155550123"
        ]
        
        for phone in valid_phones:
            assert self.plugin._is_valid_phone(phone) is True

    def test_is_valid_phone_invalid_formats(self):
        """Test phone validation with invalid formats."""
        invalid_phones = [
            "",
            "123",
            "invalid-phone",
            "(123) 45",
            "123-45-6789"
        ]
        
        for phone in invalid_phones:
            assert self.plugin._is_valid_phone(phone) is False

    def test_full_pipeline_offline(self):
        """Test complete fetch -> transform -> validate pipeline offline."""
        # Fetch mock data
        records = list(self.plugin.fetch())
        
        # Transform and validate each record
        for raw_record in records:
            transformed = self.plugin.transform(raw_record)
            is_valid = self.plugin.validate(transformed)
            
            assert is_valid is True
            assert transformed["plugin_name"] == "collab_divorce"
            assert transformed["record_type"] == "collaborative_attorney"
            assert "experience_score" in transformed
            assert transformed["experience_score"] > 0


@pytest.mark.offline
class TestCollabDivorceOfflineIntegration:
    """Integration tests that can run offline."""
    
    def test_plugin_integration_with_registry(self):
        """Test plugin can be instantiated through factory function."""
        from universal_recon.plugins.collab_divorce import get_plugin
        
        plugin = get_plugin()
        assert plugin.name == "collab_divorce"
        assert hasattr(plugin, 'fetch')
        assert hasattr(plugin, 'transform')
        assert hasattr(plugin, 'validate')

    def test_batch_processing_offline(self):
        """Test processing multiple records in batch offline."""
        plugin = CollabDivorcePlugin()
        
        # Process all mock records
        raw_records = list(plugin.fetch())
        processed_records = []
        
        for raw_record in raw_records:
            transformed = plugin.transform(raw_record)
            if plugin.validate(transformed):
                processed_records.append(transformed)
        
        assert len(processed_records) == 2
        assert all(record["plugin_name"] == "collab_divorce" for record in processed_records)
        assert all("experience_score" in record for record in processed_records)

    def test_error_handling_malformed_data(self):
        """Test plugin handles malformed input data gracefully."""
        plugin = CollabDivorcePlugin()
        
        malformed_data = {
            "name": None,
            "location": {},
            "phone": [],
            "email": 123,
            "years_experience": "invalid"
        }
        
        # Should not raise exception
        transformed = plugin.transform(malformed_data)
        is_valid = plugin.validate(transformed)
        
        # Should return a transformed record but fail validation
        assert isinstance(transformed, dict)
        assert is_valid is False