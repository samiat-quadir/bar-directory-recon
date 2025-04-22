# === analytics/domain_anomaly_flagger.py ===

import json
import argparse
from pathlib import Path


def flag_anomalies(matrix_path: str, export_path: str = None, verbose: bool = False):
    matrix = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    updated = False

    for site, data in matrix.get("sites", {}).items():
        anomalies = []

        if "bar" in data.get("domain_tags", []):
            if "bar_number" not in data.get("fields", {}):
                anomalies.append("missing_bar_number")

        if "contact" not in data.get("fields", {}):
            anomalies.append("missing_contact_field")

        if anomalies:
            data["anomaly_flags"] = anomalies
            updated = True
            if verbose:
                print(f"⚠️ {site}: {', '.join(anomalies)}")

    if updated and export_path:
        Path(export_path).write_text(json.dumps(matrix, indent=2))
        if verbose:
            print(f"\n[✓] Matrix with anomalies saved to {export_path}")
    elif not updated and verbose:
        print("✅ No anomalies detected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Domain Anomaly Flagger")
    parser.add_argument("--matrix-path", required=True, help="Path to schema_matrix.json")
    parser.add_argument("--export-json", help="Optional: write modified matrix to this file")
    parser.add_argument("--verbose", action="store_true", help="Verbose printout")
    args = parser.parse_args()

    flag_anomalies(args.matrix_path, args.export_json, args.verbose)
