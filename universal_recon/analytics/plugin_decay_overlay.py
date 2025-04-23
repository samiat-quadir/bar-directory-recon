# === analytics/plugin_decay_overlay.py ===

import json
import os
import argparse
from pathlib import Path
from typing import Dict, List
import yaml

from utils.validator_drift_badges import VALIDATOR_DRIFT_BADGES

def load_yaml(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_matrix(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_validator_plugin_map(validation_matrix: Dict) -> Dict[str, Dict]:
    mapping = {}
    for validator, meta in validation_matrix.items():
        if "plugin" in meta:
            mapping[meta["plugin"]] = {
                "validator": validator,
                "required": meta.get("plugin_required", False),
                "severity": meta.get("on_plugin_removed", "info")
            }
    return mapping

def analyze_plugin_decay(archive_dir: str, matrix_path: str, yaml_path: str) -> Dict:
    archive_files = sorted(
        [f for f in os.listdir(archive_dir) if f.endswith(".json")]
    )
    if len(archive_files) < 2:
        raise RuntimeError("Need at least two archived matrix snapshots for decay detection.")

    oldest_path = os.path.join(archive_dir, archive_files[0])
    latest = load_matrix(matrix_path)
    oldest = load_matrix(oldest_path)
    validation_matrix = load_yaml(yaml_path)
    plugin_map = get_validator_plugin_map(validation_matrix)

    result = {
        "plugin_decay": [],
        "site_summary": {}
    }

    for site, latest_info in latest.get("sites", {}).items():
        old_info = oldest.get("sites", {}).get(site, {})
        latest_plugins = set(latest_info.get("plugins_used", []))
        old_plugins = set(old_info.get("plugins_used", []))
        removed_plugins = list(old_plugins - latest_plugins)

        decay_data = []
        validator_score = 0
        for plugin in removed_plugins:
            impact = plugin_map.get(plugin)
            badge = None
            if impact:
                severity = impact.get("severity", "info")
                badge = VALIDATOR_DRIFT_BADGES.get(severity, VALIDATOR_DRIFT_BADGES["info"])
                if severity == "critical":
                    validator_score += 2
                elif severity == "warning":
                    validator_score += 1
            decay_data.append({
                "plugin": plugin,
                "linked_validator": impact["validator"] if impact else None,
                "severity": impact["severity"] if impact else "info",
                "icon": badge["icon"] if badge else "",
                "tooltip": badge["tooltip"] if badge else ""
            })

        result["plugin_decay"].append({
            "site": site,
            "removed_plugins": decay_data,
            "validator_impact_score": validator_score
        })
        result["site_summary"][site] = {
            "removed_plugin_count": len(removed_plugins),
            "validator_impact_score": validator_score
        }

    return result

def save_overlay(data: Dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Plugin decay overlay exported to: {path}")

def main():
    parser = argparse.ArgumentParser(description="Plugin Decay Overlay Generator with Validator Mapping")
    parser.add_argument("--archive-dir", default="output/archive/", help="Path to matrix archive folder")
    parser.add_argument("--matrix-path", default="output/schema_matrix.json", help="Current schema_matrix path")
    parser.add_argument("--validation-yaml", default="validators/validation_matrix.yaml", help="Path to validator mapping YAML")
    parser.add_argument("--export-json", default="output/plugin_decay_overlay.json", help="Export output JSON path")
    args = parser.parse_args()

    data = analyze_plugin_decay(
        archive_dir=args.archive_dir,
        matrix_path=args.matrix_path,
        yaml_path=args.validation_yaml
    )
    save_overlay(data, args.export_json)

if __name__ == "__main__":
    main()
