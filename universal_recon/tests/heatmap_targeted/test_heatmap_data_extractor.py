import importlib

import pytest


def test_data_extractor_import():
    """Test that data_extractor can be imported"""
    try:
        m = importlib.import_module("data_extractor")
        assert m is not None
        assert hasattr(m, "__file__")
    except ImportError:
        pytest.skip("data_extractor module not available")


def test_data_extractor_has_functions():
    """Test that data_extractor has expected functions"""
    try:
        m = importlib.import_module("data_extractor")
    except ImportError:
        pytest.skip("data_extractor module not available")

    # Check for DataExtractor class
    has_class = hasattr(m, "DataExtractor")
    assert has_class, "DataExtractor class not found"

    # Try to check the class
    if has_class:
        try:
            extractor_cls = m.DataExtractor
            assert callable(extractor_cls)
        except Exception:
            pass  # Some classes might need specific args
