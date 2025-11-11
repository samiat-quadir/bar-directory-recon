# === analytics/score_drift_export.py ===

import argparse
import csv
import json
from pathlib import Path


def generate_drift_csv(site: str, baseline_snapshot: str = None, output_dir: str = "output"):
    archive = Path(output_dir) / "archive"
    after_path = Path(output_dir) / "schema_matrix.json"

    if not archive.exists():
        raise FileNotFoundError("Archive directory not found.")

    snapshots = sorted(archive.glob("schema_matrix_*.json"))
    if not snapshots:
        raise FileNotFoundError("No snapshots found in archive.")

    before_path = None
    if baseline_snapshot:
        before_path = archive / f"schema_matrix_{baseline_snapshot}.json"
    else:
        before_path = snapshots[0]

    if not before_path.exists() or not after_path.exists():
        raise FileNotFoundError("One or more matrix files not found.")

    def extract_score(path):
        with open(path, "r", encoding="utf-8") as f:
            matrix = json.load(f)
        return matrix.get("sites", {}).get(site, {}).get("score_summary", {}).get("field_score")

    old = extract_score(before_path) or 0
    new = extract_score(after_path) or 0
    delta = round(new - old, 2)

    csv_path = Path(output_dir) / f"{site}_score_drift.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "before", "after", "delta"])
        writer.writerow([site, old, new, delta])

    print(f"[✓] Score drift exported to: {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--baseline-snapshot", default=None)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    generate_drift_csv(
        site=args.site, baseline_snapshot=args.baseline_snapshot, output_dir=args.output_dir
    )
