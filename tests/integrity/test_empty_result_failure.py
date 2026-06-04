"""
Tests for empty result failure policy - OPT-IN strict validation.

Verifies:
- Default permissive behavior (allow_empty=True)
- Strict mode error raising (allow_empty=False)
- Warning threshold logic
- Error message clarity
"""

import pytest
from policies.failure_policy import (
    FailurePolicy,
    validate_url_extraction,
    validate_record_extraction,
)


class TestFailurePolicyDefaults:
    """Test that default policy is backward-compatible (permissive)."""
    
    def test_default_policy_allows_empty_urls(self):
        """Default policy should allow empty URLs (backward compatible)."""
        policy = FailurePolicy()
        assert policy.allow_empty_urls is True
        assert policy.allow_empty_records is True
    
    def test_default_thresholds_are_reasonable(self):
        """Default warning thresholds should be sensible."""
        policy = FailurePolicy()
        assert policy.url_warning_threshold == 5
        assert policy.record_warning_threshold == 10


class TestURLValidationPermissive:
    """Test URL validation with default permissive settings."""
    
    def test_empty_urls_logs_warning_not_error(self, caplog):
        """Empty URLs should log warning but NOT raise error (default)."""
        validate_url_extraction([])  # Should not raise
        assert "Empty URL extraction" in caplog.text
        assert "WARNING" in caplog.text
    
    def test_low_url_count_triggers_warning(self, caplog):
        """URL count below threshold should log warning."""
        policy = FailurePolicy(url_warning_threshold=5)
        validate_url_extraction(["url1", "url2"], policy)
        assert "Low URL count" in caplog.text
        assert "2 URLs" in caplog.text
    
    def test_sufficient_urls_no_warning(self, caplog):
        """URL count above threshold should not log warning."""
        policy = FailurePolicy(url_warning_threshold=5)
        validate_url_extraction(["url1", "url2", "url3", "url4", "url5", "url6"], policy)
        assert "Low URL count" not in caplog.text


class TestURLValidationStrict:
    """Test URL validation with strict mode (OPT-IN)."""
    
    def test_empty_urls_raises_error_when_strict(self):
        """Empty URLs should raise ValueError when allow_empty_urls=False."""
        policy = FailurePolicy(allow_empty_urls=False)
        
        with pytest.raises(ValueError, match="allow_empty_urls=False"):
            validate_url_extraction([], policy)
    
    def test_non_empty_urls_pass_strict_mode(self):
        """Non-empty URLs should pass even in strict mode."""
        policy = FailurePolicy(allow_empty_urls=False)
        validate_url_extraction(["url1"], policy)  # Should not raise
    
    def test_error_message_includes_context(self):
        """Error message should include context for debugging."""
        policy = FailurePolicy(allow_empty_urls=False)
        
        with pytest.raises(ValueError, match="listing phase"):
            validate_url_extraction([], policy, context="listing phase")


class TestRecordValidationPermissive:
    """Test record validation with default permissive settings."""
    
    def test_empty_records_logs_warning_not_error(self, caplog):
        """Empty records should log warning but NOT raise error (default)."""
        validate_record_extraction([])  # Should not raise
        assert "Empty record extraction" in caplog.text
        assert "WARNING" in caplog.text
    
    def test_low_record_count_triggers_warning(self, caplog):
        """Record count below threshold should log warning."""
        policy = FailurePolicy(record_warning_threshold=10)
        validate_record_extraction([{"id": 1}, {"id": 2}], policy)
        assert "Low record count" in caplog.text
        assert "2 records" in caplog.text
    
    def test_sufficient_records_no_warning(self, caplog):
        """Record count above threshold should not log warning."""
        policy = FailurePolicy(record_warning_threshold=10)
        records = [{"id": i} for i in range(15)]
        validate_record_extraction(records, policy)
        assert "Low record count" not in caplog.text


class TestRecordValidationStrict:
    """Test record validation with strict mode (OPT-IN)."""
    
    def test_empty_records_raises_error_when_strict(self):
        """Empty records should raise ValueError when allow_empty_records=False."""
        policy = FailurePolicy(allow_empty_records=False)
        
        with pytest.raises(ValueError, match="allow_empty_records=False"):
            validate_record_extraction([], policy)
    
    def test_non_empty_records_pass_strict_mode(self):
        """Non-empty records should pass even in strict mode."""
        policy = FailurePolicy(allow_empty_records=False)
        validate_record_extraction([{"id": 1}], policy)  # Should not raise
    
    def test_error_message_includes_context(self):
        """Error message should include context for debugging."""
        policy = FailurePolicy(allow_empty_records=False)
        
        with pytest.raises(ValueError, match="detail phase"):
            validate_record_extraction([], policy, context="detail phase")


class TestPolicyConfiguration:
    """Test policy configuration validation."""
    
    def test_custom_thresholds_respected(self, caplog):
        """Custom thresholds should override defaults."""
        policy = FailurePolicy(url_warning_threshold=20, record_warning_threshold=30)
        
        # Should warn below threshold
        validate_url_extraction(["url1"] * 10, policy)
        assert "Low URL count" in caplog.text
        assert "10 URLs" in caplog.text
        
        caplog.clear()
        validate_record_extraction([{"id": 1}] * 15, policy)
        assert "Low record count" in caplog.text
        assert "15 records" in caplog.text
        
        # Should NOT warn at or above threshold
        caplog.clear()
        validate_url_extraction(["url1"] * 25, policy)
        assert "Low URL count" not in caplog.text
        
        caplog.clear()
        validate_record_extraction([{"id": 1}] * 35, policy)
        assert "Low record count" not in caplog.text
    
    def test_negative_threshold_raises_error(self):
        """Negative thresholds should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            FailurePolicy(url_warning_threshold=-1)
        
        with pytest.raises(ValueError, match="non-negative"):
            FailurePolicy(record_warning_threshold=-1)
    
    def test_zero_threshold_valid(self, caplog):
        """Zero threshold should be valid (disables warning)."""
        policy = FailurePolicy(url_warning_threshold=0, record_warning_threshold=0)
        
        # Should not warn even with 1 URL/record
        validate_url_extraction(["url1"], policy)
        validate_record_extraction([{"id": 1}], policy)
        assert "Low URL count" not in caplog.text
        assert "Low record count" not in caplog.text
