# analytics/score_drift_export.py

import os
import csv
import json
import argparse
from pathlib import Path
from typing import Dict

def load_snapshot(matrix_path: Path) -> Dict:
    try:
        with matrix_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load matrix: {matrix_path.name} ({e})")
        return {}

def find_snapshot_by_suffix(archive_dir: Path, suffix: str) -> Path:
    for file in archive_dir.glob(f"schema_matrix_{suffix}.json"):
        return file
    return None

def get_sorted_snapshots(archive_dir: Path):
    return sorted([f for f in archive_dir.glob("schema_matrix_*.json")])

def generate_drift_csv(site: str, output_dir: Path, baseline_suffix: str = None):
    archive_dir = Path("output/archive")
    latest_path = Path("output/schema_matrix.json")

    if baseline_suffix:
        baseline_file = find_snapshot_by_suffix(archive_dir, baseline_suffix)
    else:
        snapshots = get_sorted_snapshots(archive_dir)
        baseline_file = snapshots[0] if snapshots else None

    if not baseline_file:
        print("❌ No baseline snapshot found.")
        return

    baseline = load_snapshot(baseline_file)
    latest = load_snapshot(latest_path)

    old_site = baseline.get("sites", {}).get(site, {})
    new_site = latest.get("sites", {}).get(site, {})

    old_score = old_site.get("score_summary", {}).get("field_score")
    new_score = new_site.get("score_summary", {}).get("field_score")

    if not isinstance(old_score, (int, float)):
        old_score = 0
    if not isinstance(new_score, (int, float)):
        new_score = 0

    delta = round(new_score - old_score, 2)

    csv_path = output_dir / f"{site}_score_drift.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Site", "Old Score", "New Score", "Delta"])
        writer.writerow([site, old_score, new_score, delta])

    print(f"[✓] Score drift exported to {csv_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--baseline-snapshot", help="Filename suffix of baseline snapshot")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    generate_drift_csv(site=args.site, baseline_suffix=args.baseline_snapshot, output_dir=Path(args.output_dir))

if __name__ == "__main__":
    main()
