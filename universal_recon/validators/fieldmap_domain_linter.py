# === validators/fieldmap_domain_linter.py ===

import json
import os
from pathlib import Path

import yaml

# Load validation matrix
VALIDATION_MATRIX_PATH = Path(__file__).parent.parent / "validation_matrix.yaml"
with open(VALIDATION_MATRIX_PATH, "r", encoding="utf-8") as f:
    VALIDATION_MATRIX = yaml.safe_load(f)


def domain_lint_fieldmap(fieldmap_path, verbose=False):
    with open(fieldmap_path, encoding="utf-8") as f:
        data = json.load(f)

    domain_tags = data.get("domain_tags", [])
    fields = [f.get("name") for f in data.get("fields", [])]
    site_name = os.path.basename(fieldmap_path).replace("_fieldmap.json", "")

    anomalies = []
    flagged_validators = []

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

    if verbose:
        print(f"\n[DOMAIN LINT] Site: {site_name}")
        print(f"- Domains: {domain_tags}")
        print(f"- Anomalies: {anomalies}")
        for v in flagged_validators:
            print(f"  ⛔ {v['validator']} ({v['severity']}) – {v['description']}")

    # Inject anomaly flags back into fieldmap if needed
    data["anomaly_flags"] = anomalies
    data["validator_flags"] = flagged_validators

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
