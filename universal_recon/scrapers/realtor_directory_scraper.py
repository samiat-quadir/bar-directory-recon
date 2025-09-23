"""Entrypoint for realtor directory scraping used by imports in tests.

This module delegates to a local test-only stub if present under tools/ so
CI can avoid making network calls. In production, replace or augment this
with the real implementation.
"""

from __future__ import annotations

import importlib
from typing import Any


def scrape_realtor_directory(
    *, source_url: str | None = None, limit: int | None = None
) -> list[dict[str, Any]]:
    """Deterministic, side-effect-free entrypoint used by tests.

    Prefer the project-local tools stub (tools.realtor_directory_scraper) if
    available so we don't duplicate test-only code.
    """
    try:
        stub = importlib.import_module("tools.realtor_directory_scraper")
        if hasattr(stub, "scrape_realtor_directory"):
            return stub.scrape_realtor_directory(source_url=source_url, limit=limit)
    except Exception:
        # fall through to safe default
        pass

    # Safe default for CI: no network activity, empty result set
    return []
