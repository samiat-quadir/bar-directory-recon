# === analytics/schema_matrix_collector.py ===

import json
from pathlib import Path
from typing import Dict


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


def write_schema_matrix(
    matrix: Dict, save_path: str = "output/schema_matrix.json", verbose: bool = False
):
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)
    if verbose:
        print(f"[✓] Schema matrix written to: {save_path}")
