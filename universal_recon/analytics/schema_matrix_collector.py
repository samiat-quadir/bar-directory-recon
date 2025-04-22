# === analytics/schema_matrix_collector.py ===

import json
import os
from typing import Dict
from pathlib import Path


def collect_schema_matrix(output_dir: str = "output/fieldmap") -> Dict:
    matrix = {"sites": {}}
    fieldmap_dir = Path(output_dir)

    for file in sorted(fieldmap_dir.glob("*_fieldmap.json")):
        site_name = file.stem.replace("_fieldmap", "")
        try:
            site_data = json.loads(file.read_text(encoding="utf-8"))
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
    parser.add_argument("--output-dir", default="output/fieldmap", help="Directory with *_fieldmap.json")
    parser.add_argument("--save-path", default="output/schema_matrix.json", help="Where to save matrix")
    parser.add_argument("--verbose", action="store_true", help="Verbose print")
    args = parser.parse_args()

    matrix = collect_schema_matrix(args.output_dir)
    write_schema_matrix(matrix, args.save_path, args.verbose)
