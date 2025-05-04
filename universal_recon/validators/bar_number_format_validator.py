# validators/bar_number_format_validator.py

import re
from typing import Dict, List


def run_analysis(records=None, config=None):
    if records is None:
        records = [{"type": "bar_number", "value": "CA123456", "rank": 1, "plugin": "test"}]
    return {
        "plugin": "bar_number_format_validator",
        "results": validate_bar_numbers(records),
    }


def validate_bar_numbers(fields: List[Dict]) -> List[Dict]:
    results = []
    pattern = r"^[A-Z]{2}\d{6}$"  # Example: CA123456

    for field in fields:
        if field.get("type") != "bar_number":
            continue

        value = field.get("value", "")
        is_valid = bool(re.fullmatch(pattern, value))

        results.append(
            {
                "type": "bar_number",
                "value": value,
                "valid": is_valid,
                "error": None if is_valid else "Invalid bar number format",
                "score": 5 if is_valid else 2,
                "rank": field.get("rank", 0),
                "plugin": "bar_number_format_validator",
                "severity": "none" if is_valid else "warning",
            }
        )
    return results
