"""Firm data parser plugin for universal_recon."""

from typing import Any, Dict


def parse_firm_data(driver: Any, context: Any) -> Dict[str, Any]:
    """Parse firm data from the given driver and context.

    Args:
        driver: WebDriver instance
        context: Parsing context dictionary

    Returns:
        Dictionary containing parsed firm data
    """
    return {}


class FirmParserPlugin:
    """Minimal plugin shim used by tests to validate plugin loading/contract."""

    def __init__(self, *args, **kwargs):
        pass

    def fetch(self, **kwargs):
        """Fetch an iterator of raw firm records. Tests may monkeypatch or
        override this method when external sources are unavailable in CI."""
        # Default: return an empty iterator
        return iter([])

    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw record into normalized form."""
        # Identity transform by default
        return record

    def validate(self, record: Dict[str, Any]) -> bool:
        """Basic validation of transformed record."""
        return isinstance(record, dict)
