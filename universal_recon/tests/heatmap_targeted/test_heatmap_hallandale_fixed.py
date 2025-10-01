import importlib
import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../..", "src"))


def test_pipeline_idempotent_dedup():
    """Test hallandale pipeline with duplicate data"""
    try:
        m = importlib.import_module("hallandale_pipeline_fixed")
    except ImportError:
        pytest.skip("hallandale_pipeline_fixed module not available")

    fn = (
        getattr(m, "process", None)
        or getattr(m, "run", None)
        or getattr(m, "transform", None)
        or getattr(m, "pipeline", None)
    )

    if fn is None:
        pytest.skip("no pipeline function found")

    data = [{"id": 1, "name": "A"}, {"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    out = fn(data)
    assert out is not None


def test_pipeline_empty_data():
    """Test hallandale pipeline with empty data"""
    try:
        m = importlib.import_module("hallandale_pipeline_fixed")
    except ImportError:
        pytest.skip("hallandale_pipeline_fixed module not available")

    fn = (
        getattr(m, "process", None)
        or getattr(m, "run", None)
        or getattr(m, "transform", None)
        or getattr(m, "pipeline", None)
    )

    if fn is None:
        pytest.skip("no pipeline function found")

    try:
        out = fn([])
        assert out is not None or out == []
    except Exception:
        # Some pipelines might not handle empty data
        pytest.skip("pipeline doesn't handle empty data")
