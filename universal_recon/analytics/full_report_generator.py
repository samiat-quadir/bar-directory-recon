# full_report_generator.py

import json
import os

def run_analysis(site_name: str, output_dir: str = "output/reports") -> Dict:
    """
    Merges summary.json, audit.json, trend.json, and heatmap.json into a full report.
    Returns combined dict.
    """
    files = ["summary", "audit", "trend", "heatmap"]
    merged = {}

    for fname in files:
        path = os.path.join(output_dir, f"{site_name}_{fname}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                merged[fname] = json.load(f)
        else:
            merged[fname] = {"error": f"{fname}.json not found"}

    # Optional: Add site-level badge
    health = merged.get("template_health", {})
    status = "stable"
    for block in health.values():
        if block.get("health") == "fragile":
            status = "fragile"
            break
        elif block.get("health") == "warning":
            status = "warning"

    merged["site_health"] = status
    return merged
