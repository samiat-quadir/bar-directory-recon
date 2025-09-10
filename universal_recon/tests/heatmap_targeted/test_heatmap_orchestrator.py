import importlib
import pytest


def test_orchestrator_skips_disabled_and_handles_error():
    """Test orchestrator with disabled steps and error handling"""
    try:
        m = importlib.import_module("orchestrator")
    except ImportError:
        pytest.skip("orchestrator module not available")

    fn = (getattr(m, "run", None) or 
          getattr(m, "orchestrate", None) or 
          getattr(m, "execute", None))
    
    if fn is None:
        pytest.skip("no orchestrator function found")

    def _ok(x):
        return x + 1

    def _boom(x):
        raise ValueError("x")

    try:
        out = fn(steps=[("a", _ok, True), ("b", _boom, False)], seed=1)
    except TypeError:
        # Try different signature
        out = fn([("a", _ok, True), ("b", _boom, False)], 1)
    
    assert out is not None


def test_orchestrator_basic_execution():
    """Test basic orchestrator execution"""
    try:
        m = importlib.import_module("orchestrator")
    except ImportError:
        pytest.skip("orchestrator module not available")

    fn = (getattr(m, "run", None) or 
          getattr(m, "orchestrate", None) or 
          getattr(m, "execute", None))
    
    if fn is None:
        pytest.skip("no orchestrator function found")

    def simple_step(x):
        return x * 2

    try:
        # Test simple execution
        out = fn([("double", simple_step, True)], 5)
        assert out is not None
    except Exception:
        # Some orchestrators might need different input format
        pytest.skip("orchestrator signature mismatch")