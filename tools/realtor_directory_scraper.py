"""Test-only stub for realtor scraper to avoid network in CI."""


def scrape_realtor_directory(*args, **kwargs):
    """Return empty list for tests; replace with real implementation for scraping."""
    return []
