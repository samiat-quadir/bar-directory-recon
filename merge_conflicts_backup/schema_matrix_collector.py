# === analytics/schema_matrix_collector.py ===

import json
from pathlib import Path
<<<<<<< HEAD
from typing import Dict
=======
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
>>>>>>> 3ccf4fd (Committing all changes)


def collect_schema_matrix(output_dir: str = "output/fieldmap") -> Dict:
    matrix = {"sites": {}}
    output_path = Path(output_dir)

    for file in output_path.glob("*_fieldmap.json"):
        site = file.stem.replace("_fieldmap", "")
        try:
            with file.open("r", encoding="utf-8") as f:
                fieldmap = json.load(f)
            matrix["sites"][site] = {
                "score_summary": fieldmap.get("score_summary", {}),
                "plugins_used": fieldmap.get("plugins_used", []),
                "domain_tags": fieldmap.get("domain_tags", []),
                "anomaly_flags": fieldmap.get("anomaly_flags", []),
            }
        except Exception as e:
            matrix["sites"][site] = {"error": str(e)}

    return matrix


def write_schema_matrix(matrix: Dict, save_path: str = "output/schema_matrix.json", verbose: bool = False):
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)
    if verbose:
<<<<<<< HEAD
        print(f"[✓] Schema matrix written to: {save_path}")
=======
        print(f"[✓] Schema matrix written to {save_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Schema Matrix Collector")
    parser.add_argument("--output-dir", default="output/fieldmap", help="Directory with *_fieldmap.json")
    parser.add_argument("--save-path", default="output/schema_matrix.json", help="Where to save matrix")
    parser.add_argument("--verbose", action="store_true", help="Verbose print")
    args = parser.parse_args()

    matrix = collect_schema_matrix(args.output_dir)
    write_schema_matrix(matrix, args.save_path, args.verbose)
>>>>>>> 3ccf4fd (Committing all changes)
