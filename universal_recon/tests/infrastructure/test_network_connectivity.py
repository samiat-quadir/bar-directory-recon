"""Test network connectivity for external dependencies."""

import pytest


@pytest.mark.skip(reason="Network connectivity test - skipped in CI environment")
def test_external_api_connectivity() -> None:
    """Test connectivity to external APIs - typically skipped in CI."""
    # This test would normally check connectivity to external services
    # but is skipped in most environments to avoid network dependencies
