"""Test plugin loader functionality."""

from unittest.mock import mock_open, patch

from universal_recon.plugin_loader import load_plugins_by_type


def test_load_plugins_by_type_missing_registry():
    """Test that missing registry returns empty list."""
    with patch("os.path.exists", return_value=False):
        result = load_plugins_by_type("test_type")
        assert result == []


def test_load_plugins_by_type_invalid_json():
    """Test that invalid JSON in registry returns empty list."""
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="invalid json")),
    ):
        result = load_plugins_by_type("test_type")
        assert result == []


def test_load_plugins_by_type_unknown_plugin_safe():
    """Test that unknown plugin type handles missing modules gracefully."""
    # The loader doesn't raise exceptions; it prints warnings and continues
    with (
        patch("os.path.exists", return_value=True),
        patch(
            "builtins.open",
            mock_open(read_data='[{"type": "test", "module": "nonexistent_module"}]'),
        ),
    ):
        result = load_plugins_by_type("test")
        # Should return empty list when module can't be imported
        assert result == []
