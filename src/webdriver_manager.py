"""
DEPRECATED — this module has been renamed to driver_setup.py to avoid shadowing
the webdriver-manager PyPI package (webdriver_manager.chrome).

This shim re-exports everything from driver_setup for backwards compatibility.
Delete this file once all imports have been updated to use driver_setup directly.
"""

from driver_setup import WebDriverManager  # noqa: F401

__all__ = ["WebDriverManager"]
