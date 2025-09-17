"""Reference plugin implementation demonstrating the Plugin protocol.

This plugin serves as an example of how to implement the Plugin interface
for realtor directory data sources.
"""

from typing import Any, Dict
from collections.abc import Iterator


class RealtorPlugin:
    """Reference implementation of the Plugin protocol for realtor data."""

    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        return "reference_realtor"

    def fetch(self) -> Iterator[dict[str, Any]]:
        """Fetch raw data from the realtor source.

        Yields:
            Dict[str, Any]: Raw data records from the realtor source
        """
        # Sample data for reference implementation
        sample_data = [
            {
                "id": "realtor_001",
                "name": "John Smith",
                "office": "Smith Realty Group",
                "phone": "555-0123",
                "email": "j.smith@smithrealty.com",
                "specialties": ["residential", "commercial"],
            },
            {
                "id": "realtor_002",
                "name": "Sarah Johnson",
                "office": "Premium Properties",
                "phone": "555-0456",
                "email": "s.johnson@premiumprop.com",
                "specialties": ["luxury", "waterfront"],
            },
        ]

        yield from sample_data

    def transform(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw data into standardized format.

        Args:
            raw_data: Raw data record from fetch()

        Returns:
            Dict[str, Any]: Transformed data in standard format
        """
        # For reference implementation, pass through with minimal transformation
        return {
            "source": "reference_realtor",
            "id": raw_data.get("id"),
            "name": raw_data.get("name"),
            "company": raw_data.get("office"),
            "contact_phone": raw_data.get("phone"),
            "contact_email": raw_data.get("email"),
            "specialties": raw_data.get("specialties", []),
            "raw_data": raw_data,
        }

    def validate(self, transformed_data: dict[str, Any]) -> bool:
        """Validate that transformed data meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if data passes validation, False otherwise
        """
        # Basic validation - ensure required fields are present
        required_fields = ["source", "id", "name"]
        return all(
            field in transformed_data and transformed_data[field]
            for field in required_fields
        )
