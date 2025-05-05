# === validators/fieldmap_domain_linter.py ===

import json

<<<<<<< HEAD
=======
import os
from pathlib import Path

import yaml

>>>>>>> 3ccf4fd (Committing all changes)


<<<<<<< HEAD
def domain_lint_fieldmap(path: str, verbose=False):
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e)}
=======

def domain_lint_fieldmap(fieldmap_path, verbose=False):
    with open(fieldmap_path, encoding="utf-8") as f:
        data = json.load(f)
>>>>>>> 3ccf4fd (Committing all changes)

    domain_tags = data.get("domain_tags", [])
    fields = data.get("fields", [])
    field_names = {f.get("name") for f in fields if isinstance(f, dict)}

    anomalies = []

<<<<<<< HEAD
    if "bar" in domain_tags and "bar_number" not in field_names:
        anomalies.append("missing_bar_number")
=======
    for validator, props in VALIDATION_MATRIX.items():
        required_domains = props.get("required_if_domain", [])
        if any(tag in required_domains for tag in domain_tags):
            if validator not in fields:
                anomalies.append(f"missing_field:{validator}")
                flagged_validators.append(
                    {
                        "validator": validator,
                        "description": props.get("description", ""),
                        "severity": props.get("severity", "warning"),
                        "linked_plugin": props.get("linked_plugin", None),
                    }
                )
>>>>>>> 3ccf4fd (Committing all changes)

    if "legal" in domain_tags and "email" not in field_names:
        anomalies.append("missing_email_field")

    if anomalies:
        data["anomaly_flags"] = anomalies
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        if verbose:
            print(f"[!] Domain lint anomalies injected into {path}: {anomalies}")
    else:
        if verbose:
            print("[✓] No domain lint issues found.")

<<<<<<< HEAD
    return {"status": "complete", "flags": anomalies}
=======
    # Optionally write back (or caller can handle this)
    return data


# CLI runner
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run domain-lint check on a fieldmap")
    parser.add_argument("--path", required=True, help="Path to *_fieldmap.json")
    parser.add_argument("--export", help="Path to save updated fieldmap (optional)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    result = domain_lint_fieldmap(args.path, verbose=args.verbose)

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[✓] Updated fieldmap saved to: {args.export}")
>>>>>>> 3ccf4fd (Committing all changes)
