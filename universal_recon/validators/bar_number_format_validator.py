# File: validators/bar_number_format_validator.py

import re
from typing import Dict, Any

def validate(data: Dict[str, Any]) -> Dict[str, Any]:
    bar_number = data.get("bar_number", "")
    pattern = r"^[0-9]{5}-[A-Z]{2}$"
    is_valid = bool(re.match(pattern, bar_number))
    
    result = {
        "type": "bar_number",
        "value": bar_number,
        "valid": is_valid,
        "error": None if is_valid else "Invalid format",
        "score": 5 if is_valid else 2,
        "rank": 1,
        "plugin": "bar_number_format_validator",
        "severity": "none" if is_valid else "critical"
    }
    return result
