"""
Tests for validation threshold policy - OPT-IN quality score filtering.

Verifies:
- Default permissive behavior (min_validation_score=0)
- Strict filtering when threshold > 0
- Rejected record export logic
- ValidationSummary tracking
"""

import pytest
from policies.validation_policy import (
    ValidationPolicy,
    filter_by_validation_score,
    should_export_rejected,
)
from reports.validation_summary import ValidationSummary


class TestValidationPolicyDefaults:
    """Test that default policy is backward-compatible (no filtering)."""
    
    def test_default_policy_no_filtering(self):
        """Default policy should have min_validation_score=0 (no filtering)."""
        policy = ValidationPolicy()
        assert policy.min_validation_score == 0.0
        assert policy.export_rejected is False
    
    def test_default_score_field_name(self):
        """Default score field should be 'validation_score'."""
        policy = ValidationPolicy()
        assert policy.score_field == 'validation_score'


class TestFilteringPermissive:
    """Test filtering with default permissive settings (no filtering)."""
    
    def test_default_returns_all_records(self):
        """Default policy (min_score=0) should return all records as passed."""
        records = [
            {'id': 1, 'validation_score': 80},
            {'id': 2, 'validation_score': 30},
            {'id': 3, 'validation_score': 0},
        ]
        
        passed, rejected = filter_by_validation_score(records)
        
        assert len(passed) == 3
        assert len(rejected) == 0
        assert passed == records
    
    def test_zero_threshold_explicit(self):
        """Explicitly setting min_validation_score=0 should not filter."""
        policy = ValidationPolicy(min_validation_score=0.0)
        records = [{'id': 1, 'validation_score': 10}]
        
        passed, rejected = filter_by_validation_score(records, policy)
        
        assert len(passed) == 1
        assert len(rejected) == 0


class TestFilteringStrict:
    """Test filtering with strict mode (min_validation_score > 0)."""
    
    def test_filters_below_threshold(self):
        """Records below threshold should be rejected."""
        policy = ValidationPolicy(min_validation_score=60.0)
        records = [
            {'id': 1, 'validation_score': 80},
            {'id': 2, 'validation_score': 50},
            {'id': 3, 'validation_score': 60},
            {'id': 4, 'validation_score': 30},
        ]
        
        passed, rejected = filter_by_validation_score(records, policy)
        
        assert len(passed) == 2
        assert len(rejected) == 2
        assert passed[0]['id'] == 1
        assert passed[1]['id'] == 3
        assert rejected[0]['id'] == 2
        assert rejected[1]['id'] == 4
    
    def test_missing_score_treated_as_zero(self):
        """Records without validation_score field should be treated as score=0."""
        policy = ValidationPolicy(min_validation_score=50.0)
        records = [
            {'id': 1, 'validation_score': 60},
            {'id': 2},  # Missing score
        ]
        
        passed, rejected = filter_by_validation_score(records, policy)
        
        assert len(passed) == 1
        assert len(rejected) == 1
        assert passed[0]['id'] == 1
        assert rejected[0]['id'] == 2
    
    def test_custom_score_field(self):
        """Should support custom score field names."""
        policy = ValidationPolicy(min_validation_score=50.0, score_field='quality_score')
        records = [
            {'id': 1, 'quality_score': 60},
            {'id': 2, 'quality_score': 30},
        ]
        
        passed, rejected = filter_by_validation_score(records, policy)
        
        assert len(passed) == 1
        assert len(rejected) == 1


class TestExportRejected:
    """Test rejected record export configuration."""
    
    def test_default_no_export(self):
        """Default policy should not export rejected records."""
        policy = ValidationPolicy()
        assert should_export_rejected(policy) is False
    
    def test_export_when_enabled(self):
        """Should export rejected records when export_rejected=True."""
        policy = ValidationPolicy(export_rejected=True)
        assert should_export_rejected(policy) is True
    
    def test_export_rejected_none_policy(self):
        """should_export_rejected with None policy should return False (default)."""
        assert should_export_rejected(None) is False


class TestValidationSummary:
    """Test ValidationSummary tracking and reporting."""
    
    def test_initial_state(self):
        """New summary should start with zero counts."""
        summary = ValidationSummary()
        assert summary.total_records == 0
        assert summary.passed_validation == 0
        assert summary.failed_validation == 0
        assert summary.validation_rate == 0.0
    
    def test_track_passed_records(self):
        """Should correctly track passed records."""
        summary = ValidationSummary()
        summary.add_validation_result(passed=True)
        summary.add_validation_result(passed=True)
        
        assert summary.total_records == 2
        assert summary.passed_validation == 2
        assert summary.failed_validation == 0
        assert summary.validation_rate == 100.0
    
    def test_track_failed_records(self):
        """Should correctly track failed records with reasons."""
        summary = ValidationSummary()
        summary.add_validation_result(passed=False, reason='low_score')
        summary.add_validation_result(passed=False, reason='missing_field')
        summary.add_validation_result(passed=False, reason='low_score')
        
        assert summary.total_records == 3
        assert summary.passed_validation == 0
        assert summary.failed_validation == 3
        assert summary.validation_rate == 0.0
        assert summary.failures_by_reason['low_score'] == 2
        assert summary.failures_by_reason['missing_field'] == 1
    
    def test_mixed_results(self):
        """Should correctly calculate validation rate with mixed results."""
        summary = ValidationSummary()
        summary.add_validation_result(passed=True)
        summary.add_validation_result(passed=False, reason='low_score')
        summary.add_validation_result(passed=True)
        summary.add_validation_result(passed=False, reason='low_score')
        
        assert summary.total_records == 4
        assert summary.passed_validation == 2
        assert summary.failed_validation == 2
        assert summary.validation_rate == 50.0
    
    def test_get_summary_dict(self):
        """Should export summary as dictionary."""
        summary = ValidationSummary()
        summary.add_validation_result(passed=True)
        summary.add_validation_result(passed=False, reason='low_score')
        
        result = summary.get_summary_dict()
        
        assert result['total_records'] == 2
        assert result['passed_validation'] == 1
        assert result['failed_validation'] == 1
        assert result['validation_rate_percent'] == 50.0
        assert result['failures_by_reason'] == {'low_score': 1}
    
    def test_reset(self):
        """Should reset all counters to zero."""
        summary = ValidationSummary()
        summary.add_validation_result(passed=True)
        summary.add_validation_result(passed=False, reason='low_score')
        
        summary.reset()
        
        assert summary.total_records == 0
        assert summary.passed_validation == 0
        assert summary.failed_validation == 0
        assert summary.validation_rate == 0.0
        assert len(summary.failures_by_reason) == 0


class TestPolicyConfiguration:
    """Test policy configuration validation."""
    
    def test_negative_threshold_raises_error(self):
        """Negative min_validation_score should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            ValidationPolicy(min_validation_score=-1.0)
    
    def test_threshold_above_100_raises_error(self):
        """min_validation_score > 100 should raise ValueError."""
        with pytest.raises(ValueError, match="<= 100"):
            ValidationPolicy(min_validation_score=101.0)
    
    def test_valid_threshold_range(self):
        """Valid threshold range (0-100) should not raise error."""
        policy = ValidationPolicy(min_validation_score=50.0)
        assert policy.min_validation_score == 50.0
        
        policy = ValidationPolicy(min_validation_score=100.0)
        assert policy.min_validation_score == 100.0
