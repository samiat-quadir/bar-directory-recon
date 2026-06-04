"""
Tests for unified_schema.py - Schema mapping and record validation.

Targets:
- UnifiedDataRecord dataclass
- SchemaMapper field mapping
- Record validation
- Export functionality
- Deduplication

All tests run without network calls or credentials.
"""

import pytest
from datetime import datetime


class TestUnifiedDataRecord:
    """Tests for the UnifiedDataRecord dataclass."""

    def test_default_values(self):
        """UnifiedDataRecord should have sensible defaults."""
        from src.unified_schema import UnifiedDataRecord

        record = UnifiedDataRecord()

        assert record.name == ""
        assert record.email == ""
        assert record.phone == ""
        assert record.country == "US"
        assert record.status == "active"
        assert record.validation_score == 0.0
        assert record.practice_areas == []
        assert record.custom_fields == {}

    def test_record_with_values(self):
        """UnifiedDataRecord should accept all values."""
        from src.unified_schema import UnifiedDataRecord

        record = UnifiedDataRecord(
            name="John Doe",
            email="john@example.com",
            phone="555-123-4567",
            company="Acme Inc",
            city="Miami",
            state="FL",
            zip_code="33101",
        )

        assert record.name == "John Doe"
        assert record.email == "john@example.com"
        assert record.company == "Acme Inc"
        assert record.city == "Miami"
        assert record.state == "FL"

    def test_record_with_lists(self):
        """UnifiedDataRecord should handle list fields."""
        from src.unified_schema import UnifiedDataRecord

        record = UnifiedDataRecord(
            name="Jane Smith",
            practice_areas=["Family Law", "Estate Planning"],
            certifications=["Bar Certified", "Mediation Certified"],
        )

        assert "Family Law" in record.practice_areas
        assert len(record.certifications) == 2

    def test_record_with_custom_fields(self):
        """UnifiedDataRecord should store custom fields."""
        from src.unified_schema import UnifiedDataRecord

        record = UnifiedDataRecord(
            name="Test User",
            custom_fields={"special_id": "ABC123", "priority": "high"},
        )

        assert record.custom_fields["special_id"] == "ABC123"
        assert record.custom_fields["priority"] == "high"


class TestSchemaMapper:
    """Tests for SchemaMapper functionality."""

    def test_init_with_source_type(self):
        """SchemaMapper should initialize with source type."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper(source_type="lawyers")

        assert mapper.source_type == "lawyers"
        assert "name" in mapper.field_mapping

    def test_init_with_unknown_source_type(self):
        """SchemaMapper should handle unknown source types."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper(source_type="unknown_type")

        assert mapper.source_type == "unknown_type"
        assert mapper.field_mapping == {}

    def test_map_to_unified_basic(self):
        """map_to_unified should convert raw data to UnifiedDataRecord."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper(source_type="lawyers")
        raw_data = {
            "attorney_name": "John Smith",
            "contact_email": "john@lawfirm.com",
            "office_phone": "555-123-4567",
            "firm_name": "Smith & Associates",
        }

        record = mapper.map_to_unified(raw_data)

        assert record.name == "John Smith"
        assert record.email == "john@lawfirm.com"
        assert record.phone == "555-123-4567"
        assert record.company == "Smith & Associates"

    def test_map_to_unified_with_custom_fields(self):
        """map_to_unified should store unmapped fields in custom_fields."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper(source_type="lawyers")
        raw_data = {
            "name": "Test Attorney",
            "unmapped_field": "some value",
            "another_custom": 12345,
        }

        record = mapper.map_to_unified(raw_data)

        assert record.name == "Test Attorney"
        assert "unmapped_field" in record.custom_fields
        assert record.custom_fields["unmapped_field"] == "some value"

    def test_validate_record_valid(self):
        """validate_record should pass for valid records."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            name="John Doe",
            email="john@example.com",
            phone="555-123-4567",
            company="Test Corp",
            address="123 Main St",
            city="Miami",
            state="FL",
        )

        result = mapper.validate_record(record)

        assert result["valid"] is True
        assert result["score"] > 0
        assert len(result["issues"]) == 0

    def test_validate_record_missing_name(self):
        """validate_record should flag missing name."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            email="test@example.com",
            phone="555-123-4567",
        )

        result = mapper.validate_record(record)

        assert "Missing name" in result["issues"]
        assert result["score"] < 100

    def test_validate_record_missing_contact(self):
        """validate_record should flag missing both email and phone."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(name="John Doe")

        result = mapper.validate_record(record)

        assert "Missing both email and phone" in result["issues"]

    def test_validate_record_invalid_email(self):
        """validate_record should flag invalid email format."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            name="John Doe",
            email="not-an-email",
            phone="555-123-4567",
        )

        result = mapper.validate_record(record)

        assert "Invalid email format" in result["issues"]

    def test_validate_record_short_phone(self):
        """validate_record should flag short phone numbers."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            name="John Doe",
            email="john@example.com",
            phone="555",
        )

        result = mapper.validate_record(record)

        assert "Phone number too short" in result["issues"]


class TestSchemaMapperExport:
    """Tests for export functionality."""

    def test_to_export_dict_standard(self):
        """to_export_dict should create export dictionary."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            name="John Doe",
            email="john@example.com",
            company="Test Corp",
            city="Miami",
            state="FL",
        )

        export = mapper.to_export_dict(record, "standard")

        assert export["Full Name"] == "John Doe"
        assert export["Email Address"] == "john@example.com"
        assert export["Company/Firm"] == "Test Corp"
        assert export["City"] == "Miami"

    def test_to_export_dict_handles_lists(self):
        """to_export_dict should convert lists to comma-separated strings."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        record = UnifiedDataRecord(
            name="Jane Smith",
            practice_areas=["Tax Law", "Corporate Law"],
        )

        export = mapper.to_export_dict(record, "detailed")

        assert "Tax Law, Corporate Law" in export["Practice Areas"]

    def test_get_export_headers(self):
        """get_export_headers should return ordered headers."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper()

        headers = mapper.get_export_headers("standard")

        assert "Full Name" in headers
        assert "Email Address" in headers
        assert headers.index("Full Name") < headers.index("Email Address")


class TestSchemaMapperDeduplication:
    """Tests for deduplication functionality."""

    def test_deduplicate_records_by_email(self):
        """deduplicate_records should remove duplicates by email."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        records = [
            UnifiedDataRecord(name="John Doe", email="john@example.com"),
            UnifiedDataRecord(name="John D.", email="john@example.com"),  # Duplicate
            UnifiedDataRecord(name="Jane Smith", email="jane@example.com"),
        ]

        unique = mapper.deduplicate_records(records, dedup_fields=["email"])

        assert len(unique) == 2

    def test_deduplicate_records_by_phone(self):
        """deduplicate_records should remove duplicates by phone."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        records = [
            UnifiedDataRecord(name="John Doe", phone="555-123-4567"),
            UnifiedDataRecord(name="John D.", phone="(555) 123-4567"),  # Same number
            UnifiedDataRecord(name="Jane Smith", phone="555-999-8888"),
        ]

        unique = mapper.deduplicate_records(records, dedup_fields=["phone"])

        assert len(unique) == 2

    def test_deduplicate_records_keeps_empty(self):
        """deduplicate_records should keep records without dedup field values."""
        from src.unified_schema import SchemaMapper, UnifiedDataRecord

        mapper = SchemaMapper()
        records = [
            UnifiedDataRecord(name="John Doe"),  # No email or phone
            UnifiedDataRecord(name="Jane Smith"),  # No email or phone
            UnifiedDataRecord(name="Bob", email="bob@example.com"),
        ]

        unique = mapper.deduplicate_records(records)

        # All should be kept - first two have no dedup values
        assert len(unique) == 3


class TestSchemaMapperBatchOperations:
    """Tests for batch operations."""

    def test_map_data_to_unified_schema_list(self):
        """map_data_to_unified_schema should process list of raw data."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper(source_type="realtors")
        raw_data_list = [
            {"agent_name": "John Realtor", "contact_email": "john@realty.com"},
            {"agent_name": "Jane Agent", "contact_email": "jane@realty.com"},
        ]

        records = mapper.map_data_to_unified_schema(raw_data_list)

        assert len(records) == 2
        assert records[0].name == "John Realtor"
        assert records[1].name == "Jane Agent"

    def test_map_data_with_source_name(self):
        """map_data_to_unified_schema should add source name to raw data."""
        from src.unified_schema import SchemaMapper

        mapper = SchemaMapper()
        raw_data_list = [{"name": "Test User"}]

        records = mapper.map_data_to_unified_schema(
            raw_data_list, source_name="TestSource"
        )

        # Source name is stored in custom_fields since "source" is not in field_mapping
        # The record.source field defaults to source_type
        assert "source" in records[0].custom_fields
        assert records[0].custom_fields["source"] == "TestSource"


class TestCreateUnifiedConfigTemplate:
    """Tests for configuration template."""

    def test_create_unified_config_template(self):
        """create_unified_config_template should return valid config."""
        from src.unified_schema import create_unified_config_template

        config = create_unified_config_template()

        assert "name" in config
        assert "base_url" in config
        assert "data_schema" in config
        assert "scraping" in config
        assert "webdriver" in config
        assert "pagination" in config
        assert "output" in config
        assert "notifications" in config
        assert "logging" in config
        assert "security" in config

    def test_config_template_data_schema(self):
        """Config template should have valid data_schema section."""
        from src.unified_schema import create_unified_config_template

        config = create_unified_config_template()

        assert config["data_schema"]["source_type"] == "standard"
        assert config["data_schema"]["validation_enabled"] is True
        assert "deduplication_fields" in config["data_schema"]
