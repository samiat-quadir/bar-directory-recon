"""Base protocol for plugins in the universal reconnaissance system.

This module defines the Plugin protocol that all plugins must implement.
Using typing.Protocol for duck typing - plugins don't need to inherit,
just implement the required methods with correct signatures.
"""

from typing import Any, Dict, Protocol
from collections.abc import Iterator


class Plugin(Protocol):
    """Protocol defining the interface all plugins must implement."""

    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        ...

    def fetch(self) -> Iterator[dict[str, Any]]:
        """Fetch raw data from the source.

        Yields:
            Dict[str, Any]: Raw data records from the source
        """
        ...

    def transform(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw data into standardized format.

        Args:
            raw_data: Raw data record from fetch()

        Returns:
            Dict[str, Any]: Transformed data in standard format
        """
        ...

    def validate(self, transformed_data: dict[str, Any]) -> bool:
        """Validate that transformed data meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if data passes validation, False otherwise
        """
        ...
