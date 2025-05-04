# === analytics/schema_score_linter.py ===

import json
from pathlib import Path


def score_fieldmap(fieldmap_path: str, verbose: bool = False) -> dict:
    """
    Computes a schema completeness score from a fieldmap JSON file.
    """
    path = Path(fieldmap_path)
    if not path.exists():
        raise FileNotFoundError(f"Fieldmap not found: {fieldmap_path}")

    with path.open("r", encoding="utf-8") as f:
        fieldmap = json.load(f)

    required_fields = ["name", "email", "phone", "bar_number"]
    found_fields = fieldmap.get("fields", [])
    score = (len(set(found_fields) & set(required_fields)) / len(required_fields)) * 100

    fieldmap["score_summary"] = {"field_score": round(score, 2)}

    with path.open("w", encoding="utf-8") as f:
        json.dump(fieldmap, f, indent=2)

    if verbose:
        print(f"[✓] Fieldmap scored: {fieldmap_path} → {score:.2f}")

    return fieldmap["score_summary"]
