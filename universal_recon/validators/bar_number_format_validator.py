# validators/bar_number_format_validator.py

import re
from typing import Dict

BAR_PATTERN = r"^\d{5}-[A-Z]{2}$"

def validate_bar_number(record: Dict) -> Dict:
    value = record.get("value", "")
    plugin = "bar_number_format_validator"
    is_valid = bool(re.match(BAR_PATTERN, value))

    return {
        "type": "bar_number",
        "value": value,
        "valid": is_valid,
        "error": None if is_valid else "Invalid bar number format",
        "score": 5 if is_valid else 2,
        "rank": 1,
        "plugin": plugin,
        "severity": "none" if is_valid else "critical"
    }
