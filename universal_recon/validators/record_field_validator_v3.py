# universal_recon/validators/record_field_validator_v3.py

import re
from validators.validation_matrix import load_validation_matrix

def run_field_validators(fieldmap, verbose=False):
    matrix = load_validation_matrix()
    results = []
    for field in fieldmap.get("fields", []):
        field_name = field.get("name")
        if not field_name:
            continue

        if verbose:
            print(f"[•] Validating field: {field_name}")

        for validator_id, validator_def in matrix.items():
            applies_to = validator_def.get("applies_to", [])
            if field_name not in applies_to:
                continue

            # Apply simple rule checks
            rule = validator_def.get("rule")
            passed = True
            if rule == "must_have_example":
                passed = bool(field.get("example"))
            elif rule == "must_be_email":
                example = field.get("example", "")
                passed = re.match(r"[^@]+@[^@]+\.[^@]+", example) is not None

            results.append({
                "field": field_name,
                "validator": validator_id,
                "passed": passed,
                "severity": validator_def.get("severity", "info"),
                "description": validator_def.get("description", "")
            })

    return results
