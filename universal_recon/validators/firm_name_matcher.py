# validators/firm_name_matcher.py

from typing import Dict

def validate_firm_name(record: Dict) -> Dict:
    value = record.get("value", "").strip()
    plugin = "firm_name_matcher"
    is_valid = len(value) > 3 and not value.lower().startswith("unknown")

    return {
        "type": "firm_name",
        "value": value,
        "valid": is_valid,
        "error": None if is_valid else "Firm name too short or missing",
        "score": 5 if is_valid else 3,
        "rank": 1,
        "plugin": plugin,
        "severity": "none" if is_valid else "warning"
    }
