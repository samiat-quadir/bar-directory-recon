"""Test realtor directory scraper functionality."""
from universal_recon.scrapers.realtor_directory_scraper import scrape_realtor_directory


def test_scraper_returns_empty_list_for_ci():
    """Test that scraper returns empty list in CI environment (no network)."""
    result = scrape_realtor_directory()
    assert isinstance(result, list)
    assert result == []


def test_scraper_handles_optional_parameters():
    """Test that scraper handles optional source_url and limit parameters."""
    result = scrape_realtor_directory(source_url="http://test.com", limit=10)
    assert isinstance(result, list)
    assert result == []


def test_scraper_with_keyword_args():
    """Test that scraper accepts keyword arguments properly."""
    result = scrape_realtor_directory(source_url=None, limit=None)
    assert isinstance(result, list)
    assert result == []

