# === validators/fieldmap_validator.py ===

import json


def validate_fieldmap(path: str, verbose=False):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return {"valid": False, "error": f"Could not read fieldmap: {e}"}

    if not isinstance(data, dict):
        return {"valid": False, "error": "Fieldmap is not a JSON object"}

    if "fields" not in data:
        return {"valid": False, "error": "Missing 'fields' key"}

    if not isinstance(data["fields"], list):
        return {"valid": False, "error": "'fields' should be a list"}

    if verbose:
        print(f"[✓] Fieldmap at {path} passed structural validation.")
    return {"valid": True}
