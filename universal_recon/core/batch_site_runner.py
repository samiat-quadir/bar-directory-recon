import json
import os
from typing import Dict, List

from utils.recon_trend_tracker import analyze_trends


def run_batch_sites(site_names: List[str], output_dir: str = "output/reports") -> Dict[str, Dict]:
    aggregate = {}
    for site in site_names:
        site_file = os.path.join(output_dir, f"{site}_summary.json")
        if not os.path.exists(site_file):
            print(f"[batch_runner] Summary not found for {site}, skipping...")
            continue

        with open(site_file, "r", encoding="utf-8") as f:
            site_summary = json.load(f)

        aggregate[site] = site_summary

        # Run trend tracker if data exists
        try:
            analyze_trends(site_name=site)
        except Exception as e:
            print(f"[batch_runner] Trend analysis failed for {site}: {e}")

    # Save aggregated results
    aggregate_path = os.path.join(output_dir, "aggregate_summary.json")
    with open(aggregate_path, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)

    print(f"\n📊 Batch complete. Summary saved to {aggregate_path}")
    return aggregate
