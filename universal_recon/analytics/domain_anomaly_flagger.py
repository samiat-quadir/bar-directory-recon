# === analytics/domain_anomaly_flagger.py ===

import json
from pathlib import Path


def flag_anomalies(
    fieldmap_dir="output/fieldmap",
    output_path="output/reports/domain_anomalies.json",
    verbose=False,
):
    output = {"anomalies": []}
    fieldmap_dir = Path(fieldmap_dir)
    for file in fieldmap_dir.glob("*_fieldmap.json"):
        site = file.stem.replace("_fieldmap", "")
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        missing = []
        if "bar" in data.get("domain_tags", []):
            if "bar_number" not in data.get("fields", []):
                missing.append("bar_number")
        if "email" not in data.get("fields", []):
            missing.append("email")
        if missing:
            output["anomalies"].append(
                {
                    "site": site,
                    "missing_fields": missing,
                    "domain_tags": data.get("domain_tags", []),
                }
            )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    if verbose:
        print(f"[✓] Domain anomaly flags saved to: {output_path}")
