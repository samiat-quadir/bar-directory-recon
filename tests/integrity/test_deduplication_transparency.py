"""
Test: Deduplication Transparency

Verifies that duplicate removal is logged and reported, not silent.
"""

import pytest
from pathlib import Path
from reports.deduplication_report import (
    DeduplicationReport,
    deduplicate_with_tracking
)


class TestDeduplicationTransparency:
    """Tests for transparent deduplication reporting."""
    
    def test_track_url_deduplication_counts(self):
        """Should track total vs unique counts."""
        report = DeduplicationReport()
        
        original = ['url1', 'url2', 'url1', 'url3', 'url2', 'url4']
        unique = ['url1', 'url2', 'url3', 'url4']
        
        report.track_url_deduplication(original, unique)
        
        assert report.url_total == 6
        assert report.url_unique == 4
        assert len(report.url_duplicates) == 2  # Two duplicate occurrences
    
    def test_no_duplicates_reports_zero(self):
        """Should correctly report when no duplicates found."""
        report = DeduplicationReport()
        
        urls = ['url1', 'url2', 'url3']
        
        report.track_url_deduplication(urls, urls)
        
        assert report.url_total == 3
        assert report.url_unique == 3
        assert len(report.url_duplicates) == 0
    
    def test_get_summary_includes_percentages(self):
        """Summary should include removal percentage."""
        report = DeduplicationReport()
        
        original = ['url1', 'url2', 'url1', 'url3', 'url1']
        unique = ['url1', 'url2', 'url3']
        
        report.track_url_deduplication(original, unique)
        summary = report.get_summary()
        
        assert summary['urls']['total'] == 5
        assert summary['urls']['unique'] == 3
        assert summary['urls']['duplicates_removed'] == 2
        assert summary['urls']['removal_percentage'] == 40.0
    
    def test_save_report_creates_json_file(self, tmp_path):
        """Should save deduplication report to JSON file."""
        report = DeduplicationReport()
        
        original = ['url1', 'url2', 'url1']
        unique = ['url1', 'url2']
        
        report.track_url_deduplication(original, unique)
        
        report_path = report.save_report(tmp_path, 'test_scrape')
        
        assert report_path.exists()
        assert report_path.name == 'test_scrape_deduplication_report.json'
        
        # Verify JSON is valid
        import json
        with open(report_path) as f:
            data = json.load(f)
        
        assert data['urls']['total'] == 3
        assert data['urls']['unique'] == 2
    
    def test_report_includes_duplicate_examples(self, tmp_path):
        """Report should include examples of duplicates."""
        report = DeduplicationReport()
        
        original = ['url1', 'url2', 'url1', 'url3', 'url2']
        unique = ['url1', 'url2', 'url3']
        
        report.track_url_deduplication(original, unique)
        report_path = report.save_report(tmp_path, 'test')
        
        import json
        with open(report_path) as f:
            data = json.load(f)
        
        assert 'url_duplicate_examples' in data
        assert len(data['url_duplicate_examples']) > 0
        assert 'url1' in data['url_duplicate_examples']
    
    def test_deduplicate_with_tracking_preserves_order(self):
        """deduplicate_with_tracking should preserve first occurrence order."""
        report = DeduplicationReport()
        
        items = ['url3', 'url1', 'url2', 'url1', 'url3']
        
        unique = deduplicate_with_tracking(items, report)
        
        # Order should be: url3, url1, url2 (first occurrence order)
        assert unique == ['url3', 'url1', 'url2']
        assert report.url_total == 5
        assert report.url_unique == 3
    
    def test_deduplicate_with_tracking_updates_report(self):
        """deduplicate_with_tracking should update the report object."""
        report = DeduplicationReport()
        
        items = ['a', 'b', 'a', 'c', 'b', 'a']
        
        unique = deduplicate_with_tracking(items, report)
        summary = report.get_summary()
        
        assert len(unique) == 3
        assert summary['urls']['duplicates_removed'] == 3
        assert summary['urls']['removal_percentage'] == 50.0
    
    def test_log_summary_outputs_deduplication_info(self, caplog):
        """log_summary should output deduplication statistics."""
        import logging
        caplog.set_level(logging.INFO)
        
        report = DeduplicationReport()
        
        original = ['url1', 'url2', 'url1', 'url3']
        unique = ['url1', 'url2', 'url3']
        
        report.track_url_deduplication(original, unique)
        
        logger = logging.getLogger('test')
        report.log_summary(logger)
        
        # Check log contains key information
        log_output = ' '.join([r.message for r in caplog.records])
        assert '4 total' in log_output or '3 unique' in log_output
    
    def test_empty_list_deduplication(self):
        """Should handle empty list without error."""
        report = DeduplicationReport()
        
        report.track_url_deduplication([], [])
        summary = report.get_summary()
        
        assert summary['urls']['total'] == 0
        assert summary['urls']['unique'] == 0
        assert summary['urls']['removal_percentage'] == 0
