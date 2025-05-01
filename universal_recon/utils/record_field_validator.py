# utils/record_field_validator.py

"""
Validates record structures against the ADA schema.
Use this to enforce consistency, check plugins, or verify output.

Supports:
  - strict mode: raises errors on violations
  - soft mode: logs warnings, fills missing optional fields
"""

REQUIRED_FIELDS = ["type", "value", "xpath", "context", "url"]
OPTIONAL_FIELDS = ["confidence", "source", "category"]
VALID_TYPES = {"email", "phone", "possible_name", "labeled_field"}


def validate(record, strict=False, logger=None):
    """
    Validate a single record against the ADA schema.

    Params:
        record: dict
        strict: bool → if True, raises ValueError on issues
        logger: callable → optional logging function

    Returns:
        bool → True if valid, False if corrected or invalid (non-strict)
    """
    valid = True

    # Check required fields
    for key in REQUIRED_FIELDS:
        if key not in record:
            msg = f"[Validator] Missing required field: {key}"
            if strict:
                raise ValueError(msg)
            if logger:
                logger(msg, level="WARN")
            record[key] = ""  # fallback
            valid = False

    # Check known type
    rtype = record.get("type", "")
    if rtype not in VALID_TYPES:
        msg = f"[Validator] Invalid type: {rtype}"
        if strict:
            raise ValueError(msg)
        if logger:
            logger(msg, level="WARN")
        record["type"] = "unknown"
        valid = False

    # Add optional fields if missing
    for opt in OPTIONAL_FIELDS:
        record.setdefault(opt, None)

    return valid


def validate_all(records, strict=False, logger=None):
    """
    Validate a list of records.

    Params:
        records: list[dict]
        strict: bool
        logger: callable

    Returns:
        tuple: (valid_records, invalid_count)
    """
    valid_records = []
    invalid_count = 0
    for rec in records:
        try:
            if validate(rec, strict=strict, logger=logger):
                valid_records.append(rec)
            else:
                valid_records.append(rec)
                invalid_count += 1
        except ValueError as e:
            invalid_count += 1
            if logger:
                logger(f"[Validator] Strict mode error: {e}", level="ERROR")
            if not strict:
                valid_records.append(rec)
    return valid_records, invalid_count
