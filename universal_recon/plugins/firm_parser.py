"""Firm data parser plugin for universal_recon."""

from typing import Any, Dict, Iterator


class FirmParserPlugin:
    """Plugin for parsing firm data from various sources."""

    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        return "firm_parser"

    def fetch(self) -> Iterator[Dict[str, Any]]:
        """Fetch raw firm data from the source.

        Yields:
            Dict[str, Any]: Raw firm data records
        """
        # Sample firm data for testing - replace with actual data source
        sample_firms = [
            {
                "name": "Tech Solutions Inc",
                "industry": "Technology",
                "location": "San Francisco, CA",
                "employees": 150,
                "revenue": "10M"
            },
            {
                "name": "Green Energy Corp",
                "industry": "Energy",
                "location": "Austin, TX",
                "employees": 75,
                "revenue": "5M"
            },
            {
                "name": "Financial Advisors LLC",
                "industry": "Finance",
                "location": "New York, NY",
                "employees": 250,
                "revenue": "25M"
            }
        ]

        for firm in sample_firms:
            yield firm

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw firm data into standardized format.

        Args:
            raw_data: Raw firm data record from fetch()

        Returns:
            Dict[str, Any]: Transformed data in standard format
        """
        # Standardize the firm data format
        transformed = {
            "company_name": raw_data.get("name", "").strip(),
            "industry_sector": raw_data.get("industry", "Unknown"),
            "headquarters": raw_data.get("location", ""),
            "employee_count": self._parse_employee_count(raw_data.get("employees")),
            "annual_revenue": self._parse_revenue(raw_data.get("revenue")),
            "data_source": "firm_parser",
            "record_type": "company_profile"
        }
        return transformed

    def validate(self, transformed_data: Dict[str, Any]) -> bool:
        """Validate that transformed firm data meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if data passes validation, False otherwise
        """
        # Basic validation checks
        required_fields = ["company_name", "industry_sector"]

        # Check required fields are present and non-empty
        for field in required_fields:
            if not transformed_data.get(field):
                return False

        # Check employee count is reasonable (if provided)
        employee_count = transformed_data.get("employee_count")
        if employee_count is not None and (employee_count < 0 or employee_count > 1000000):
            return False

        return True

    def _parse_employee_count(self, employees: Any) -> int:
        """Parse employee count from various formats."""
        if isinstance(employees, int):
            return employees
        elif isinstance(employees, str):
            # Remove common suffixes and convert
            clean = employees.replace(",", "").replace("+", "").strip()
            try:
                return int(clean)
            except ValueError:
                return 0
        return 0

    def _parse_revenue(self, revenue: Any) -> str:
        """Parse revenue into standardized string format."""
        if isinstance(revenue, str):
            return revenue.strip()
        elif isinstance(revenue, (int, float)):
            return f"${revenue:,.0f}"
        return "Unknown"


def parse_firm_data(driver: Any, context: Any) -> Dict[str, Any]:
    """Legacy function for backward compatibility.

    Args:
        driver: WebDriver instance
        context: Parsing context dictionary

    Returns:
        Dictionary containing parsed firm data
    """
    # This maintains backward compatibility with existing code
    plugin = FirmParserPlugin()
    # Return the first transformed record for compatibility
    for raw_record in plugin.fetch():
        if plugin.validate(raw_record):
            return plugin.transform(raw_record)
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
