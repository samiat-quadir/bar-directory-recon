"""
Test: Output File Collision Prevention

Verifies that output files generated in rapid succession do not overwrite each other.
"""

import pytest
from pathlib import Path
import time
from policies.export_policy import ExportPolicy


class TestOutputCollisionPrevention:
    """Tests for preventing output file overwrites."""
    
    def test_uuid_strategy_generates_unique_filenames(self):
        """UUID strategy should generate different filenames each time."""
        policy = ExportPolicy(collision_strategy='uuid')
        
        filename1 = policy.generate_safe_filename('test_export', 'csv')
        filename2 = policy.generate_safe_filename('test_export', 'csv')
        
        assert filename1 != filename2
        assert filename1.startswith('test_export_')
        assert filename2.startswith('test_export_')
        assert filename1.endswith('.csv')
        assert filename2.endswith('.csv')
    
    def test_millisecond_strategy_includes_milliseconds(self):
        """Millisecond strategy should include millisecond precision in timestamp."""
        policy = ExportPolicy(collision_strategy='millisecond')
        
        filename = policy.generate_safe_filename('test_export', 'csv')
        
        # Filename should have format: test_export_YYYYMMDD_HHMMSS_mmm.csv
        parts = filename.replace('.csv', '').split('_')
        
        # Should have at least: base, date, time, milliseconds
        assert len(parts) >= 4
        
        # Millisecond part should be 3 digits
        ms_part = parts[-1]
        assert len(ms_part) == 3
        assert ms_part.isdigit()
    
    def test_increment_strategy_avoids_existing_files(self, tmp_path):
        """Increment strategy should detect existing files and increment."""
        policy = ExportPolicy(collision_strategy='increment', include_timestamp=False)
        
        # Create first file
        filename1 = policy.generate_safe_filename('export', 'csv', tmp_path)
        file1 = tmp_path / filename1
        file1.touch()
        
        # Generate second filename - should increment
        filename2 = policy.generate_safe_filename('export', 'csv', tmp_path)
        
        assert filename1 == 'export.csv'
        assert filename2 == 'export_v1.csv'
    
    def test_increment_strategy_multiple_collisions(self, tmp_path):
        """Increment strategy should handle multiple existing files."""
        policy = ExportPolicy(collision_strategy='increment', include_timestamp=False)
        
        # Create multiple existing files
        (tmp_path / 'export.csv').touch()
        (tmp_path / 'export_v1.csv').touch()
        (tmp_path / 'export_v2.csv').touch()
        
        # Next filename should be v3
        filename = policy.generate_safe_filename('export', 'csv', tmp_path)
        
        assert filename == 'export_v3.csv'
    
    def test_timestamp_can_be_disabled(self):
        """Should be able to generate filename without timestamp."""
        policy = ExportPolicy(
            collision_strategy='uuid',
            include_timestamp=False
        )
        
        filename = policy.generate_safe_filename('export', 'csv')
        
        # Should only have base name and UUID (no timestamp)
        parts = filename.replace('.csv', '').split('_')
        assert len(parts) == 2  # base + uuid
        assert parts[0] == 'export'
    
    def test_invalid_strategy_raises_error(self):
        """Invalid collision strategy should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ExportPolicy(collision_strategy='invalid')
        
        assert 'Invalid collision_strategy' in str(exc_info.value)
    
    def test_different_extensions_supported(self):
        """Should support different file extensions."""
        policy = ExportPolicy(collision_strategy='uuid')
        
        csv_file = policy.generate_safe_filename('export', 'csv')
        json_file = policy.generate_safe_filename('export', 'json')
        xlsx_file = policy.generate_safe_filename('export', 'xlsx')
        
        assert csv_file.endswith('.csv')
        assert json_file.endswith('.json')
        assert xlsx_file.endswith('.xlsx')
    
    def test_rapid_generation_no_collision_uuid(self):
        """Generating many filenames rapidly should not produce duplicates (UUID)."""
        policy = ExportPolicy(collision_strategy='uuid')
        
        filenames = set()
        for _ in range(100):
            filename = policy.generate_safe_filename('export', 'csv')
            filenames.add(filename)
        
        # All 100 filenames should be unique
        assert len(filenames) == 100
    
    def test_rapid_generation_no_collision_millisecond(self):
        """Generating filenames rapidly with millisecond precision (with small delay)."""
        policy = ExportPolicy(collision_strategy='millisecond')
        
        filenames = []
        for _ in range(5):
            filename = policy.generate_safe_filename('export', 'csv')
            filenames.append(filename)
            time.sleep(0.001)  # 1ms delay
        
        # Most filenames should be different (millisecond precision)
        unique_count = len(set(filenames))
        assert unique_count >= 3  # At least some should be unique
