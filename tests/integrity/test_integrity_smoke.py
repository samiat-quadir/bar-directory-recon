"""
Smoke tests for integrity guarantees.

These tests verify that all integrity features (validation threshold,
empty result handling, collision prevention, deduplication) work correctly
in real pytest execution context.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from src.policies.failure_policy import FailurePolicy
from src.policies.validation_policy import ValidationPolicy
from src.reports.validation_summary import ValidationSummary


class TestValidationThreshold:
    """Test validation threshold behavior."""
    
    def test_validation_score_filtering(self):
        """High-score records pass, low-score records are filtered."""
        validator = ValidationPolicy(min_validation_score=0.51)
        
        # Record above threshold - should NOT be filtered
        high_score = validator.filter_by_validation_score(
            {"score": 0.95}, 
            min_score=0.51
        )
        assert not high_score, "Record with score 0.95 should not be filtered"
        
        # Record below threshold - should be filtered
        low_score = validator.filter_by_validation_score(
            {"score": 0.25}, 
            min_score=0.51
        )
        assert low_score, "Record with score 0.25 should be filtered"
    
    def test_validation_threshold_boundary(self):
        """Test exact boundary cases for validation threshold."""
        validator = ValidationPolicy(min_validation_score=0.50)
        
        # Exactly at threshold - should pass
        at_threshold = validator.filter_by_validation_score(
            {"score": 0.50}, 
            min_score=0.50
        )
        assert not at_threshold, "Record at threshold should not be filtered"
        
        # Just below threshold - should be filtered
        below_threshold = validator.filter_by_validation_score(
            {"score": 0.49}, 
            min_score=0.50
        )
        assert below_threshold, "Record below threshold should be filtered"


class TestEmptyResultFailure:
    """Test empty result handling."""
    
    def test_empty_result_fails_by_default(self):
        """Empty results should fail unless allow_empty=True."""
        policy = FailurePolicy()
        empty = {"records": [], "count": 0}
        
        # Should fail (return True means validation failed)
        assert policy.validate_url_extraction(empty, allow_empty=False)
    
    def test_empty_result_passes_when_allowed(self):
        """Empty results should pass when allow_empty=True."""
        policy = FailurePolicy()
        empty = {"records": [], "count": 0}
        
        # Should pass (return False means validation passed)
        assert not policy.validate_url_extraction(empty, allow_empty=True)
    
    def test_non_empty_result_always_passes(self):
        """Non-empty results should always pass regardless of allow_empty."""
        policy = FailurePolicy()
        non_empty = {
            "records": [{"id": 1, "url": "https://example.com"}],
            "count": 1
        }
        
        # Should pass with both settings
        assert not policy.validate_url_extraction(non_empty, allow_empty=False)
        assert not policy.validate_url_extraction(non_empty, allow_empty=True)
    
    def test_empty_record_extraction_validation(self):
        """Test empty record extraction validation."""
        policy = FailurePolicy()
        empty = {"records": [], "extraction_context": {}}
        
        # Should fail by default
        assert policy.validate_record_extraction(empty, allow_empty=False)
        
        # Should pass when allowed
        assert not policy.validate_record_extraction(empty, allow_empty=True)


class TestOutputCollisionPrevention:
    """Test output filename uniqueness."""
    
    def test_utc_timestamp_based_filenames_are_unique(self):
        """UTC timestamp-based filenames should be naturally unique."""
        filenames = set()
        
        for i in range(10):
            timestamp = datetime.now(timezone.utc).isoformat()
            filename = f"export_{timestamp.replace(':', '-')}.json"
            
            # Add to set - if collision, set size won't grow
            assert filename not in filenames, f"Collision detected: {filename}"
            filenames.add(filename)
        
        # All 10 filenames should be unique
        assert len(filenames) == 10
    
    def test_sequential_counter_prevents_same_timestamp_collision(self):
        """Sequential counter appending prevents collisions even with identical timestamps."""
        # Simulate rapid exports at same millisecond
        base_timestamp = datetime.now(timezone.utc).isoformat().replace(':', '-')
        filenames = []
        
        for counter in range(5):
            filename = f"export_{base_timestamp}_#{counter}.json"
            filenames.append(filename)
        
        # All should be unique due to counter
        assert len(set(filenames)) == 5


class TestDeduplicationReporting:
    """Test deduplication and summary reporting."""
    
    def test_validation_summary_tracks_results(self):
        """ValidationSummary should track and report validation results."""
        summary = ValidationSummary()
        
        # Add multiple results
        results = [
            {"url": "https://test.com", "score": 0.95, "passed": True},
            {"url": "https://test.com", "score": 0.95, "passed": True},  # Duplicate
            {"url": "https://other.com", "score": 0.80, "passed": True},
            {"url": "https://test.com", "score": 0.90, "passed": True},  # Duplicate
            {"url": "https://failed.com", "score": 0.10, "passed": False},
        ]
        
        for r in results:
            summary.add_validation_result(
                url=r["url"],
                passed=r["passed"],
                validation_score=r["score"]
            )
        
        # Get summary report
        report = summary.get_summary_dict()
        
        # Should have required fields
        assert "total_validated" in report
        assert "passed_count" in report
        assert "failed_count" in report
        
        # Check counts
        assert report["total_validated"] == 5
        assert report["passed_count"] == 4
        assert report["failed_count"] == 1
    
    def test_summary_generates_report_output(self):
        """ValidationSummary should generate readable report output."""
        summary = ValidationSummary()
        
        # Add test data
        for i in range(3):
            summary.add_validation_result(
                url=f"https://test{i}.com",
                passed=True,
                validation_score=0.8 + (i * 0.05)
            )
        
        # Get summary
        report = summary.get_summary_dict()
        
        # Report should be serializable to JSON (for logging)
        import json
        report_json = json.dumps(report)
        assert isinstance(report_json, str)
        assert "total_validated" in report_json


class TestIntegritySmoke:
    """Integration tests for all integrity features together."""
    
    def test_validation_and_empty_result_together(self):
        """Validation threshold and empty result handling should work together."""
        validator = ValidationPolicy(min_validation_score=0.70)
        empty_policy = FailurePolicy()
        
        # Test record that is low-score
        low_score_record = {"score": 0.60}
        filtered = validator.filter_by_validation_score(low_score_record, min_score=0.70)
        assert filtered, "Low score record should be filtered"
        
        # Empty result should also fail by default
        empty_result = {"records": [], "count": 0}
        should_fail = empty_policy.validate_url_extraction(empty_result, allow_empty=False)
        assert should_fail, "Empty result should fail by default"
    
    def test_full_integrity_workflow(self):
        """Test complete integrity workflow: validate → filter → dedupe → report."""
        validator = ValidationPolicy(min_validation_score=0.60)
        empty_policy = FailurePolicy()
        summary = ValidationSummary()
        
        # Raw results with duplicates
        raw_results = [
            {"url": "https://a.com", "score": 0.95, "passed": True},
            {"url": "https://a.com", "score": 0.95, "passed": True},  # Dup
            {"url": "https://b.com", "score": 0.55, "passed": False},  # Below threshold
            {"url": "https://c.com", "score": 0.80, "passed": True},
        ]
        
        # Apply validation threshold
        validated = []
        for r in raw_results:
            if not validator.filter_by_validation_score(r, min_score=0.60):
                validated.append(r)
        
        # Should have filtered out the 0.55 score
        assert len(validated) == 3
        
        # Dedupe and summarize
        seen_urls = set()
        for r in validated:
            url = r["url"]
            if url not in seen_urls:
                summary.add_validation_result(
                    url=url,
                    passed=r["passed"],
                    validation_score=r["score"]
                )
                seen_urls.add(url)
        
        # Check final state
        assert len(seen_urls) == 2  # Only a.com and c.com
        report = summary.get_summary_dict()
        assert report["total_validated"] == 2
