"""Tests for logging configuration."""
import os
import logging
import pytest
from pathlib import Path
from src.utils.logging.config import setup_logging, setup_default_logging

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary logging config file."""
    config_content = """
version: 1
disable_existing_loggers: false
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
root:
  level: INFO
  handlers: [console]
"""
    config_file = tmp_path / "test_logging.yaml"
    config_file.write_text(config_content)
    return config_file

def test_setup_logging_with_config(temp_config_file, caplog):
    """Test logging setup with valid config file."""
    setup_logging(str(temp_config_file))
    logging.info("Test log message")
    assert "Test log message" in caplog.text

def test_setup_logging_without_config(caplog):
    """Test logging setup with missing config file."""
    setup_logging("nonexistent.yaml")
    logging.info("Test default log message")
    assert "Test default log message" in caplog.text
    assert "Using default logging configuration" in caplog.text

def test_setup_default_logging(caplog):
    """Test default logging configuration."""
    setup_default_logging(level=logging.DEBUG)
    logging.debug("Test debug message")
    assert "Test debug message" in caplog.text