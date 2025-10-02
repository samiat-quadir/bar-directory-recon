# universal_recon/analytics/schema_score_linter.py

import json
import os


def run_schema_score_lint(site_name, verbose=False):
    fieldmap_path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
    if not os.path.exists(fieldmap_path):
        print(f"[!] Fieldmap not found: {fieldmap_path}")
        return None

    with open(fieldmap_path, encoding="utf-8") as f:
        fieldmap = json.load(f)

    # Simple mock scoring logic
    fields = fieldmap.get("fields", [])
    score = 100
    deductions = []

    for field in fields:
        if not field.get("example"):
            score -= 10
            deductions.append(f"Missing example: {field['name']}")

    result = {"site": site_name, "final_score": max(0, score), "deductions": deductions}

    if verbose:
        print(f"[✓] Schema score lint complete: {result}")

    return result
