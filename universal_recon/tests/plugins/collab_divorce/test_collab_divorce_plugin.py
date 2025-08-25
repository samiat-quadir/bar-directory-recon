"""Tests for the collaborative divorce plugin."""

import importlib
import pytest
from unittest.mock import Mock

def test_collab_divorce_plugin_loads():
    """Test that the collab_divorce plugin can be imported and has required class."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    assert hasattr(m, 'CollabDivorcePlugin')
    
    # Ensure the plugin has required methods
    plugin = m.CollabDivorcePlugin()
    assert hasattr(plugin, 'name')
    assert hasattr(plugin, 'fetch')
    assert hasattr(plugin, 'transform')
    assert hasattr(plugin, 'validate')
    assert plugin.name == "collab_divorce"


def test_collab_divorce_plugin_contract_smoke():
    """Test the full fetch -> transform -> validate pipeline for collab_divorce plugin."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()

    validated_records = []
    raw_records = []
    
    # Test fetch() returns iterator
    for raw_record in plugin.fetch():
        assert isinstance(raw_record, dict)
        raw_records.append(raw_record)
        
        # Test transform() processes raw data
        transformed = plugin.transform(raw_record)
        assert isinstance(transformed, dict)
        
        # Test validate() accepts/rejects data
        is_valid = plugin.validate(transformed)
        assert isinstance(is_valid, bool)
        
        if is_valid:
            validated_records.append(transformed)
    
    # Ensure we got some data through the pipeline
    assert len(raw_records) > 0, "Plugin should return at least one raw record"
    assert len(validated_records) > 0, "Plugin should produce at least one valid record"
    
    # Verify transformed records have expected structure
    sample_record = validated_records[0]
    required_fields = ["professional_name", "professional_type", "data_source", "record_type"]
    for field in required_fields:
        assert field in sample_record, f"Missing required field: {field}"
    
    assert sample_record["data_source"] == "collab_divorce"
    assert sample_record["record_type"] == "collaborative_professional"


def test_collab_divorce_phone_formatting():
    """Test phone number formatting functionality."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    # Test various phone number formats
    test_cases = [
        ("(206) 555-0123", "(206) 555-0123"),  # Already formatted
        ("2065550123", "(206) 555-0123"),      # 10 digits
        ("12065550123", "(206) 555-0123"),     # 11 digits with 1
        ("206-555-0123", "(206) 555-0123"),    # Dashes
        ("206.555.0123", "(206) 555-0123"),    # Dots
        ("", ""),                               # Empty
        ("invalid", "invalid"),                 # Invalid format
    ]
    
    for input_phone, expected in test_cases:
        result = plugin._format_phone(input_phone)
        assert result == expected, f"Phone formatting failed for {input_phone}"


def test_collab_divorce_validation():
    """Test validation logic for different record types."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    # Valid record
    valid_record = {
        "professional_name": "Dr. Test Professional",
        "professional_type": "collaborative_attorney",
        "contact_email": "test@example.com"
    }
    assert plugin.validate(valid_record) == True
    
    # Missing required field
    invalid_record_1 = {
        "professional_type": "collaborative_attorney"
        # Missing professional_name
    }
    assert plugin.validate(invalid_record_1) == False
    
    # Invalid professional type
    invalid_record_2 = {
        "professional_name": "Dr. Test",
        "professional_type": "invalid_type"
    }
    assert plugin.validate(invalid_record_2) == False
    
    # Invalid email format
    invalid_record_3 = {
        "professional_name": "Dr. Test",
        "professional_type": "divorce_coach",
        "contact_email": "not-an-email"
    }
    assert plugin.validate(invalid_record_3) == False


def test_collab_divorce_legacy_function():
    """Test backward compatibility function."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    
    # Mock driver and context (not used in current implementation)
    mock_driver = Mock()
    mock_context = {"test": "context"}
    
    result = m.extract_collab_divorce_data(mock_driver, mock_context)
    
    # Should return a dictionary
    assert isinstance(result, dict)
    
    # If data is returned, it should be valid
    if result:
        assert "professional_name" in result
        assert "professional_type" in result
        assert result.get("data_source") == "collab_divorce"


def test_collab_divorce_transform_edge_cases():
    """Test transform method with various edge cases."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    # Empty input
    empty_result = plugin.transform({})
    assert isinstance(empty_result, dict)
    assert empty_result["professional_name"] == ""
    assert empty_result["data_source"] == "collab_divorce"
    
    # Input with extra whitespace
    whitespace_input = {
        "name": "  Dr. Spaced Name  ",
        "email": "  EMAIL@EXAMPLE.COM  "
    }
    whitespace_result = plugin.transform(whitespace_input)
    assert whitespace_result["professional_name"] == "Dr. Spaced Name"
    assert whitespace_result["contact_email"] == "email@example.com"
    
    # Input with missing optional fields
    minimal_input = {
        "name": "Minimal Professional",
        "type": "mediator"
    }
    minimal_result = plugin.transform(minimal_input)
    assert minimal_result["professional_name"] == "Minimal Professional"
    assert minimal_result["professional_type"] == "mediator"
    assert minimal_result["certifications"] == []
    assert minimal_result["practice_areas"] == []


if __name__ == "__main__":
    pytest.main([__file__])