"""Test suite for plugin usage diff functionality."""

import json
import os
import tempfile
from unittest import TestCase
import pytest
from unittest.mock import patch

from universal_recon.analytics.plugin_usage_diff import load_plugins, main

@pytest.mark.analytics
class TestPluginUsageDiff(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def test_load_plugins_with_valid_json(self):
        """Test loading plugins from a valid JSON file."""
        test_data = {
            "plugins_used": ["plugin1", "plugin2", "plugin3"]
        }
        test_file = os.path.join(self.temp_dir, "test_fieldmap.json")
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
            
        plugins = load_plugins(test_file)
        self.assertEqual(plugins, {"plugin1", "plugin2", "plugin3"})
        
    def test_load_plugins_with_missing_file(self):
        """Test graceful handling of missing file."""
        plugins = load_plugins("nonexistent.json")
        self.assertEqual(plugins, set())
        
    def test_load_plugins_with_invalid_json(self):
        """Test handling of invalid JSON content."""
        test_file = os.path.join(self.temp_dir, "invalid.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("invalid json")
            
        plugins = load_plugins(test_file)
        self.assertEqual(plugins, set())

    def test_cli_plugin_diff(self):
        """Test CLI-based plugin diff calculation."""
        # Create test files
        before_path = os.path.join(self.temp_dir, "before.json")
        after_path = os.path.join(self.temp_dir, "after.json")
        diff_path = os.path.join(self.temp_dir, "diff.json")
        
        with open(before_path, "w", encoding="utf-8") as f:
            json.dump({"plugins_used": ["common", "removed"]}, f)
        with open(after_path, "w", encoding="utf-8") as f:
            json.dump({"plugins_used": ["common", "added"]}, f)

        # Mock sys.argv for CLI test
        test_args = [
            "plugin_usage_diff.py",
            "--before", before_path,
            "--after", after_path,
            "--export-json", diff_path
        ]
        
        with patch("sys.argv", test_args):
            main()
            
        # Verify diff results
        self.assertTrue(os.path.exists(diff_path))
        with open(diff_path, "r", encoding="utf-8") as f:
            diff_results = json.load(f)
            
        self.assertEqual(set(diff_results["missing_plugins"]), {"removed"})
        self.assertEqual(set(diff_results["added_plugins"]), {"added"})
        self.assertEqual(diff_results["before_schema"], before_path)
        self.assertEqual(diff_results["after_schema"], after_path)
        
    def tearDown(self):
        """Clean up temporary test files."""
        for f in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)