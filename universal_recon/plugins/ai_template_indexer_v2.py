"""AI Template Indexer Plugin - Convert grouped records into classified templates.

This plugin classifies grouped records (template blocks) into profile templates
such as individual, firm, hybrid, or unknown based on field composition.
"""

from typing import Any, Dict, List
from collections.abc import Iterator


class AITemplateIndexerPlugin:
    """Plugin for classifying grouped records into profile templates."""

    @property
    def name(self) -> str:
        """Return the plugin's unique identifier name."""
        return "ai_template_indexer"

    def fetch(self) -> Iterator[dict[str, Any]]:
        """Fetch raw data from input source.

        Note: This plugin operates on pre-grouped data passed via context.
        In practice, this would receive grouped records from previous processing stages.

        Yields:
            Dict[str, Any]: Grouped record template blocks
        """
        # Sample grouped data for demonstration
        sample_groups = [
            {
                "group_id": "template_001",
                "fields": [
                    {"type": "name", "value": "John Smith"},
                    {"type": "email", "value": "j.smith@example.com"},
                    {"type": "bar_number", "value": "12345"},
                    {"type": "phone", "value": "555-0123"},
                ],
            },
            {
                "group_id": "template_002",
                "fields": [
                    {"type": "firm_name", "value": "Smith & Associates"},
                    {"type": "phone", "value": "555-0456"},
                    {"type": "address", "value": "123 Main St"},
                ],
            },
            {
                "group_id": "template_003",
                "fields": [
                    {"type": "name", "value": "Sarah Johnson"},
                    {"type": "firm_name", "value": "Johnson Law Group"},
                    {"type": "email", "value": "s.johnson@jlg.com"},
                    {"type": "phone", "value": "555-0789"},
                ],
            },
        ]

        yield from sample_groups

    def transform(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform grouped record into classified template.

        Args:
            raw_data: Grouped record data from fetch()

        Returns:
            Dict[str, Any]: Template with classification and scoring
        """
        template = raw_data.copy()
        field_types = {
            field["type"] for field in raw_data.get("fields", []) if "type" in field
        }

        # Classification rules based on field composition
        if {"name", "email", "bar_number"}.issubset(field_types):
            template_type = "individual"
        elif {"firm_name", "phone"}.issubset(field_types):
            template_type = "firm"
        elif "name" in field_types and "firm_name" in field_types:
            template_type = "hybrid"
        else:
            template_type = "unknown"

        # Calculate template score (completeness signal)
        template_score = (
            len(field_types) / 8.0
        )  # normalized against expected max fields

        # Determine confidence level
        if template_score > 0.75:
            template_confidence = "high"
        elif template_score > 0.5:
            template_confidence = "medium"
        else:
            template_confidence = "low"

        # Add classification metadata
        template.update(
            {
                "template_type": template_type,
                "template_score": template_score,
                "template_confidence": template_confidence,
                "field_count": len(field_types),
                "field_types": list(field_types),
                "source": "ai_template_indexer",
            }
        )

        return template

    def validate(self, transformed_data: dict[str, Any]) -> bool:
        """Validate that template classification meets quality requirements.

        Args:
            transformed_data: Output from transform()

        Returns:
            bool: True if template passes validation, False otherwise
        """
        # Check required fields are present
        required_fields = [
            "template_type",
            "template_score",
            "template_confidence",
            "source",
        ]
        if not all(field in transformed_data for field in required_fields):
            return False

        # Validate template_type is one of expected values
        valid_types = {"individual", "firm", "hybrid", "unknown"}
        if transformed_data["template_type"] not in valid_types:
            return False

        # Validate template_score is reasonable (0.0 to 1.0)
        score = transformed_data["template_score"]
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
            return False

        # Validate confidence level
        valid_confidence = {"high", "medium", "low"}
        if transformed_data["template_confidence"] not in valid_confidence:
            return False

        return True


# Legacy function for backward compatibility
def apply(records: list[dict], context: str = "ai_template_indexer") -> list[dict]:
    """Legacy function - maintained for backward compatibility.

    Args:
        records: List of grouped record dictionaries
        context: Processing context string

    Returns:
        List[Dict]: Processed templates with classifications
    """
    plugin = AITemplateIndexerPlugin()
    results = []

    for record in records:
        transformed = plugin.transform(record)
        if plugin.validate(transformed):
            results.append(transformed)

    return results
