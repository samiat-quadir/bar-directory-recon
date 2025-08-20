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

    def parse(self, driver: Any, context: Any) -> Dict[str, Any]:
        return parse_firm_data(driver, context)
