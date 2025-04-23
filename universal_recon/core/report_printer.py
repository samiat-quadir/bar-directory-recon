# === core/report_printer.py ===

import json
from pathlib import Path

def print_summary_report(report_data: dict, site_name: str = ""):
    print(f"\n📋 Summary Report for {site_name}:")
    score = report_data.get("score_summary", {}).get("field_score")
    anomalies = report_data.get("anomaly_flags", [])
    validators = report_data.get("validator_results", {})

    if score is not None:
        print(f"  🔢 Field Score: {score:.2f}")
    if anomalies:
        print(f"  ❗ Anomalies Detected: {len(anomalies)}")
    if validators:
        failed = [k for k, v in validators.items() if not v.get("pass", True)]
        print(f"  🧪 Validators Failed: {len(failed)} / {len(validators)}")

    print("")

def save_summary_json(report_data: dict, save_path: str, verbose: bool = False):
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    if verbose:
        print(f"[✓] Report written to {save_path}")
