# universal_recon/utils/record_field_validator_v2.py

from typing import List, Dict

REQUIRED_FIELDS = ["type", "value", "xpath", "context", "url"]
OPTIONAL_FIELDS = ["confidence", "source", "category", "score", "rank", "strongest"]

# Field-specific constraints (can expand)
FIELD_RULES = {
    "email": {"must_include": "@", "min_len": 5},
    "phone": {"min_len": 7},
    "bar_number": {"min_len": 3},
    # etc.
}

def validate_records(records: List[Dict], strict: bool = False) -> List[Dict]:
    """
    Validates a list of normalized and ranked records.
    Adds 'valid': True/False and optional 'error' message.
    """
    validated = []

    for rec in records:
        record = rec.copy()
        errors = []

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in record or not record[field]:
                errors.append(f"Missing required field: {field}")

        # Field-specific logic
        type_ = record.get("type")
        value = str(record.get("value", ""))

        if type_ in FIELD_RULES:
            rules = FIELD_RULES[type_]
            if "min_len" in rules and len(value) < rules["min_len"]:
                errors.append(f"{type_} too short")
            if "must_include" in rules and rules["must_include"] not in value:
                errors.append(f"{type_} missing required pattern")

        # Set validation result
        record["valid"] = len(errors) == 0
        if not record["valid"]:
            record["error"] = "; ".join(errors)

        validated.append(record)

        # Raise exception if strict mode is on
        if strict and not record["valid"]:
            raise ValueError(f"Strict validation failed: {record.get('error')}")

    return validated
