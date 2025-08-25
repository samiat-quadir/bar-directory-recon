from __future__ import annotations

"""Tiny secrets helper. Reads environment variables; never commits secrets.

Usage:
    from universal_recon.util.secrets import get_secret
    key = get_secret("SCRAPER_API_KEY")  # returns None if unset
"""
import os
from typing import Optional


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return the environment variable value for `name` or `default`.

    Treat empty strings and a commonly-used placeholder as unset. This
    function intentionally avoids any network or filesystem access so it
    can be safely imported in test-time environments.
    """
    val = os.getenv(name)
    if val in (None, "", "PLACEHOLDER_FOR_NOW"):
        return default
    return val
