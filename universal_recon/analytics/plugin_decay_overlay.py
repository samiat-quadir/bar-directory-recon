# === analytics/plugin_decay_overlay.py ===

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_plugin_usage_snapshots(archive_dir: str):
    """Scans archive dir for schema_matrix snapshots and extracts plugin usage."""
    snapshots = []
    for fname in sorted(os.listdir(archive_dir)):
        if not fname.startswith("schema_matrix_") or not fname.endswith(".json"):
            continue
        timestamp = fname.replace("schema_matrix_", "").replace(".json", "")
        path = Path(archive_dir) / fname
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for site, site_data in data.get("sites", {}).items():
            plugins = site_data.get("plugins_used", [])
            snapshots.append({
                "timestamp": timestamp,
                "site": site,
                "plugins_used": plugins
            })
    return snapshots


def calculate_plugin_decay(snapshots):
    """Returns a dict: plugin → {total_count, site_usage_by_snapshot}"""
    plugin_data = defaultdict(lambda: {
        "total": 0,
        "timeline": defaultdict(int),
        "sites": defaultdict(list)
    })

    for snap in snapshots:
        site = snap["site"]
        time = snap["timestamp"]
        for plugin in snap.get("plugins_used", []):
            plugin_data[plugin]["total"] += 1
            plugin_data[plugin]["timeline"][time] += 1
            plugin_data[plugin]["sites"][site].append(time)

    return plugin_data


def write_decay_json(plugin_data, export_path="output/plugin_decay_overlay.json"):
    export = []
    for plugin, data in plugin_data.items():
        export.append({
            "plugin": plugin,
            "total_usages": data["total"],
            "usage_by_snapshot": dict(data["timeline"]),
            "used_on_sites": dict(data["sites"])
        })

    Path(export_path).parent.mkdir(parents=True, exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)
    print(f"[✓] Plugin decay overlay exported to {export_path}")


def main():
    parser = argparse.ArgumentParser(description="Plugin Decay Tracker – Cross-Snapshot Plugin Usage")
    parser.add_argument("--archive-dir", default="output/archive/", help="Directory of archived schema_matrix files")
    parser.add_argument("--export-json", default="output/plugin_decay_overlay.json", help="Output file path")
    args = parser.parse_args()

    snapshots = load_plugin_usage_snapshots(args.archive_dir)
    if not snapshots:
        print("⚠️ No valid snapshots found.")
        return

    plugin_data = calculate_plugin_decay(snapshots)
    write_decay_json(plugin_data, args.export_json)


if __name__ == "__main__":
    main()
