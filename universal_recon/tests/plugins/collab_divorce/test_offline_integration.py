"""Offline integration tests for collab_divorce plugin.

These tests verify the plugin works correctly without external dependencies
and can be run in CI environments.
"""

import importlib
import pytest
from typing import Dict, Any


def test_collab_divorce_offline_data_processing():
    """Test processing of offline/sample data through the plugin pipeline."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    # Simulate offline data processing
    processed_records = []
    
    for raw_record in plugin.fetch():
        # Each record should be processable offline
        transformed = plugin.transform(raw_record)
        
        # Validation should work offline
        if plugin.validate(transformed):
            processed_records.append(transformed)
    
    # Verify we processed multiple records
    assert len(processed_records) >= 3, "Should process at least 3 sample records"
    
    # Verify record diversity (different professional types)
    professional_types = set(record["professional_type"] for record in processed_records)
    assert len(professional_types) >= 2, "Should have multiple professional types"
    
    # Verify data quality
    for record in processed_records:
        assert record["professional_name"], "All records should have names"
        assert record["professional_type"] in [
            "collaborative_attorney", "divorce_coach", "financial_specialist"
        ], f"Unexpected professional type: {record['professional_type']}"


def test_collab_divorce_offline_error_handling():
    """Test plugin handles errors gracefully in offline mode."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    # Test with malformed data
    malformed_data = [
        None,
        {},
        {"invalid": "data"},
        {"name": None, "type": None},
        {"name": "", "type": ""},
    ]
    
    for bad_data in malformed_data:
        try:
            if bad_data is not None:
                transformed = plugin.transform(bad_data)
                # Transform should not crash, even with bad data
                assert isinstance(transformed, dict)
                
                # Validation should properly reject bad data
                is_valid = plugin.validate(transformed)
                # Most malformed data should fail validation
                if bad_data == {}:
                    assert not is_valid, "Empty data should fail validation"
        except Exception as e:
            pytest.fail(f"Plugin should handle malformed data gracefully: {e}")


def test_collab_divorce_offline_plugin_consistency():
    """Test plugin behavior is consistent across multiple calls."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    
    # Create multiple plugin instances
    plugin1 = m.CollabDivorcePlugin()
    plugin2 = m.CollabDivorcePlugin()
    
    # Should have consistent names
    assert plugin1.name == plugin2.name == "collab_divorce"
    
    # Should return same sample data (for testing consistency)
    records1 = list(plugin1.fetch())
    records2 = list(plugin2.fetch())
    
    assert len(records1) == len(records2), "Multiple instances should return same number of records"
    
    # Verify records are equivalent (order might vary)
    names1 = set(record.get("name", "") for record in records1)
    names2 = set(record.get("name", "") for record in records2)
    assert names1 == names2, "Multiple instances should return same professional names"


def test_collab_divorce_offline_performance():
    """Test plugin performance with offline data."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    import time
    
    # Time the full pipeline
    start_time = time.time()
    
    processed_count = 0
    for raw_record in plugin.fetch():
        transformed = plugin.transform(raw_record)
        plugin.validate(transformed)
        processed_count += 1
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Should process records efficiently
    assert processed_count > 0, "Should process at least one record"
    assert processing_time < 1.0, f"Processing should be fast, took {processing_time:.3f}s"
    
    # Performance should be reasonable per record
    avg_time_per_record = processing_time / processed_count
    assert avg_time_per_record < 0.1, f"Per-record processing too slow: {avg_time_per_record:.3f}s"


def test_collab_divorce_offline_data_quality():
    """Test data quality metrics for offline sample data."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    quality_metrics = {
        "total_records": 0,
        "valid_records": 0,
        "records_with_phone": 0,
        "records_with_email": 0,
        "records_with_certifications": 0,
        "unique_locations": set()
    }
    
    for raw_record in plugin.fetch():
        quality_metrics["total_records"] += 1
        
        transformed = plugin.transform(raw_record)
        
        if plugin.validate(transformed):
            quality_metrics["valid_records"] += 1
            
            if transformed.get("contact_phone"):
                quality_metrics["records_with_phone"] += 1
            
            if transformed.get("contact_email"):
                quality_metrics["records_with_email"] += 1
            
            if transformed.get("certifications"):
                quality_metrics["records_with_certifications"] += 1
            
            if transformed.get("location"):
                quality_metrics["unique_locations"].add(transformed["location"])
    
    # Quality assertions
    assert quality_metrics["total_records"] >= 3, "Should have multiple sample records"
    assert quality_metrics["valid_records"] == quality_metrics["total_records"], "All sample data should be valid"
    assert quality_metrics["records_with_phone"] >= 2, "Most records should have phone numbers"
    assert quality_metrics["records_with_email"] >= 2, "Most records should have email addresses"
    assert len(quality_metrics["unique_locations"]) >= 2, "Should have professionals from multiple locations"


def test_collab_divorce_offline_schema_compliance():
    """Test that all output records comply with expected schema."""
    m = importlib.import_module('universal_recon.plugins.collab_divorce')
    plugin = m.CollabDivorcePlugin()
    
    expected_fields = {
        "professional_name": str,
        "professional_type": str,
        "specialization": str,
        "location": str,
        "contact_phone": str,
        "contact_email": str,
        "certifications": list,
        "practice_areas": list,
        "data_source": str,
        "record_type": str
    }
    
    for raw_record in plugin.fetch():
        transformed = plugin.transform(raw_record)
        
        # Check all expected fields are present
        for field_name, field_type in expected_fields.items():
            assert field_name in transformed, f"Missing field: {field_name}"
            assert isinstance(transformed[field_name], field_type), \
                f"Field {field_name} should be {field_type}, got {type(transformed[field_name])}"
        
        # Check required values
        assert transformed["data_source"] == "collab_divorce"
        assert transformed["record_type"] == "collaborative_professional"


if __name__ == "__main__":
    pytest.main([__file__])