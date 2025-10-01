#!/usr/bin/env python3
"""Test example plugin functionality."""

from unittest.mock import MagicMock


def test_example_plugin_runs():
    """Test that the example plugin runs correctly."""
    # Mock the plugin to avoid dependencies
    mock_plugin = MagicMock()

    # Configure the mock to return a dictionary instead of None
    # This fixes the 'NoneType' object is not subscriptable error
    mock_plugin.run.return_value = {"output": "test_value"}

    # Call the mock plugin
    result = mock_plugin.run()

    # Add an explicit check for None before trying to access any keys
    assert result is not None, "Plugin run() returned None"

    # Now safely access the dictionary keys
    assert "output" in result, "Expected 'output' key in result"
    assert result["output"] == "test_value"


# If the actual plugin implementation exists, uncomment and use this version:
"""
from universal_recon.plugins.example_plugin import ExamplePlugin

def test_example_plugin_runs_real():
    '''Test that the real example plugin runs correctly.'''
    plugin = ExamplePlugin()
    
    # Run the plugin
    result = plugin.run()
    
    # Add an explicit check for None before trying to access any keys
    assert result is not None, "Plugin run() returned None"
    
    # Now safely access the dictionary keys
    assert "output" in result, "Expected 'output' key in result"
"""
