# === analytics/schema_score_linter.py ===

import json

<<<<<<< HEAD
from pathlib import Path

=======
import os

>>>>>>> 3ccf4fd (Committing all changes)


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

<<<<<<< HEAD
    with path.open("w", encoding="utf-8") as f:
        json.dump(fieldmap, f, indent=2)
=======
    result = {"site": site_name, "final_score": max(0, score), "deductions": deductions}
>>>>>>> 3ccf4fd (Committing all changes)

    if verbose:
        print(f"[✓] Fieldmap scored: {fieldmap_path} → {score:.2f}")

    return fieldmap["score_summary"]
