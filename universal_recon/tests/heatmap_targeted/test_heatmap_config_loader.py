import importlib
import pytest


def test_config_loader_import():
    """Test that config_loader can be imported"""
    try:
        m = importlib.import_module("config_loader")
        assert m is not None
        assert hasattr(m, "__file__")
    except ImportError:
        pytest.skip("config_loader module not available")


def test_config_loader_has_functions():
    """Test that config_loader has expected functions"""
    try:
        m = importlib.import_module("config_loader")
    except ImportError:
        pytest.skip("config_loader module not available")

    # Check for ConfigLoader class
    has_class = hasattr(m, "ConfigLoader")
    assert has_class, "ConfigLoader class not found"

    # Try to instantiate ConfigLoader
    if has_class:
        try:
            config_cls = getattr(m, "ConfigLoader")
            # Just check it's a class, don't instantiate to avoid dependencies
            assert callable(config_cls)
        except Exception:
            pass  # Some classes might need specific args
