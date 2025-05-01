# === analytics/schema_matrix_collector.py ===

import json
import os
from pathlib import Path
from typing import Any, Dict


def extract_plugins_used(site_data: Dict[str, Any]) -> list[str]:
    """
    Extract unique plugin names from plugin fieldmap records.
    """
    plugins = set()

    # Check for records
    records = site_data.get("records", [])
    if isinstance(records, list):
        for record in records:
            plugin_name = record.get("plugin")
            if plugin_name:
                plugins.add(plugin_name)

    # Fallback: if merged structure (e.g. plugin in top-level)
    if "plugin" in site_data:
        plugins.add(site_data["plugin"])

    return sorted(plugins)


def collect_schema_matrix(output_dir: str = "output/fieldmap") -> Dict:
    """
    Aggregates all *_fieldmap.json files into a full schema matrix.
    Includes plugins_used[] field if possible.
    """
    matrix = {"sites": {}}
    fieldmap_dir = Path(output_dir)

    for file in sorted(fieldmap_dir.glob("*_fieldmap.json")):
        site_name = file.stem.replace("_fieldmap", "")
        try:
            site_data = json.loads(file.read_text(encoding="utf-8"))

            # Infer plugin usage
            plugins_used = extract_plugins_used(site_data)
            site_data["plugins_used"] = plugins_used

            matrix["sites"][site_name] = site_data

        except Exception as e:
            print(f"[!] Failed to load {file.name}: {e}")

    return matrix


def write_schema_matrix(matrix: Dict, save_path: str, verbose: bool = False):
    Path(save_path).write_text(json.dumps(matrix, indent=2))
    if verbose:
        print(f"[✓] Schema matrix written to {save_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Schema Matrix Collector")
    parser.add_argument(
        "--output-dir", default="output/fieldmap", help="Directory with *_fieldmap.json"
    )
    parser.add_argument(
        "--save-path", default="output/schema_matrix.json", help="Where to save matrix"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose print")
    args = parser.parse_args()

    matrix = collect_schema_matrix(args.output_dir)
    write_schema_matrix(matrix, args.save_path, args.verbose)
