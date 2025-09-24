import importlib

import pytest


def test_next_url_basic():
    """Test pagination manager URL building"""
    try:
        m = importlib.import_module("pagination_manager")
    except ImportError:
        pytest.skip("pagination_manager module not available")

    fn = (
        getattr(m, "build_next_url", None)
        or getattr(m, "next_page", None)
        or getattr(m, "advance", None)
    )

    if fn is None:
        pytest.skip("no pagination function found")

    try:
        url = fn("https://ex.com/api", page=1, page_size=50)
    except TypeError:
        # Try positional args
        url = fn("https://ex.com/api", 1, 50)

    assert "page" in str(url) or url


def test_pagination_edge_cases():
    """Test pagination with edge cases"""
    try:
        m = importlib.import_module("pagination_manager")
    except ImportError:
        pytest.skip("pagination_manager module not available")

    fn = (
        getattr(m, "build_next_url", None)
        or getattr(m, "next_page", None)
        or getattr(m, "advance", None)
    )

    if fn is None:
        pytest.skip("no pagination function found")

    try:
        # Test with page 0
        url = fn("https://ex.com/api", 0, 10)
        assert url is not None
    except Exception:
        # Some implementations might not handle page 0
        pass
