"""Test core logger functionality."""
from universal_recon.core.logger import get_logger


def test_get_logger_returns_logger():
    """Test that get_logger returns a logger instance."""
    logger = get_logger("test")
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')


def test_get_logger_with_different_names():
    """Test that get_logger handles different logger names."""
    logger1 = get_logger("test1")
    logger2 = get_logger("test2")
    assert logger1 is not None
    assert logger2 is not None