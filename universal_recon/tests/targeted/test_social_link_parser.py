"""Test social link parser plugin functionality."""
from unittest.mock import Mock

from universal_recon.plugins.social_link_parser import apply


def test_social_link_parser_empty_html():
    """Test that social link parser handles empty HTML gracefully."""
    mock_driver = Mock()
    mock_driver.page_source = "<html><body></body></html>"
    mock_driver.current_url = "http://test.com"

    result = apply(mock_driver, "test_context")
    assert isinstance(result, list)
    assert result == []


def test_social_link_parser_detects_linkedin():
    """Test that social link parser detects LinkedIn URLs."""
    mock_driver = Mock()
    mock_driver.page_source = '<html><body><a href="https://linkedin.com/in/testuser">LinkedIn</a></body></html>'
    mock_driver.current_url = "http://test.com"

    result = apply(mock_driver, "test_context")
    assert len(result) == 1
    assert result[0]["type"] == "social"
    assert result[0]["category"] == "linkedin"
    assert result[0]["confidence"] == 1.0


def test_social_link_parser_detects_twitter():
    """Test that social link parser detects Twitter URLs."""
    mock_driver = Mock()
    mock_driver.page_source = '<html><body><a href="https://twitter.com/testuser">Twitter</a></body></html>'
    mock_driver.current_url = "http://test.com"

    result = apply(mock_driver, "test_context")
    assert len(result) == 1
    assert result[0]["type"] == "social"
    assert result[0]["category"] == "twitter"
    assert result[0]["source"] == "social_link_parser"


def test_social_link_parser_ignores_twitter_share():
    """Test that social link parser ignores Twitter share URLs."""
    mock_driver = Mock()
    mock_driver.page_source = '<html><body><a href="https://twitter.com/share">Share</a></body></html>'
    mock_driver.current_url = "http://test.com"

    result = apply(mock_driver, "test_context")
    assert result == []
