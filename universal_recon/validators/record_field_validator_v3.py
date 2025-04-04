from typing import Dict

def validate(data: Dict) -> Dict:
    """
    Validates a record's fields. Stub version.
    """
    value = data.get("field", "")
    result = {
        "type": "record_field",
        "value": value,
        "valid": bool(value),
        "error": None if value else "Missing value",
        "score": 3 if value else 0,
        "rank": 1,
        "plugin": "record_field_validator_v3",
        "severity": "warning" if not value else "none"
    }
    return result
