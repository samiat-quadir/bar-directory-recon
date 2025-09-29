# === analytics/schema_dashboard_stub.py ===

import argparse
import json
from pathlib import Path


def summarize_sites(matrix_path: str, export_path: str = None, verbose: bool = False):
    matrix = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    summary = []

    for site, data in matrix.get("sites", {}).items():
        summary.append(
            {
                "site": site,
                "field_score": data.get("score_summary", {}).get("field_score", 0),
                "plugin_count": len(data.get("plugins_used", [])),
                "domain_tags": data.get("domain_tags", []),
                "validation_status": data.get("validation_status", "unknown"),
            }
        )

    if verbose:
        print("\n📊 Schema Dashboard Summary:")
        for item in summary:
            print(
                f"  • {item['site']}: {item['field_score']} pts, {item['plugin_count']} plugins"
            )

    if export_path:
        Path(export_path).write_text(json.dumps(summary, indent=2))
        if verbose:
            print(f"\n[✓] Schema dashboard summary saved to {export_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schema Dashboard Stub")
    parser.add_argument(
        "--matrix-path", required=True, help="Path to schema_matrix.json"
    )
    parser.add_argument("--export-json", help="Output path for dashboard summary")
    parser.add_argument("--verbose", action="store_true", help="Verbose printout")
    args = parser.parse_args()

    summarize_sites(args.matrix_path, args.export_json, args.verbose)
