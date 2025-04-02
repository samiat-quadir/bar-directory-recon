# validators/record_field_validator_v3.py

import re
from typing import List, Dict

def validate_records(records: List[Dict], strict: bool = False, verbose: bool = False) -> List[Dict]:
    validated = []
    for record in records:
        r_type = record.get("type")
        value = record.get("value", "").strip()
        plugin = "record_field_validator_v3"

        result = {
            "type": r_type,
            "value": value,
            "valid": True,
            "error": None,
            "score": 5,
            "rank": 1,
            "plugin": plugin,
            "severity": "none"
        }

        if not value:
            result.update({
                "valid": False,
                "error": "Missing value",
                "score": 1,
                "severity": "critical"
            })
        elif r_type == "email" and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", value):
            result.update({
                "valid": False,
                "error": "Invalid email format",
                "score": 2,
                "severity": "critical"
            })
        elif r_type == "phone" and len(re.sub(r"\D", "", value)) < 10:
            result.update({
                "valid": False,
                "error": "Phone number too short",
                "score": 3,
                "severity": "warning"
            })

        if strict and not result["valid"]:
            continue

        validated.append({**record, **result})

    return validated
