# === analytics/schema_dashboard_stub.py ===

<<<<<<< HEAD
import json

=======
import argparse
import json
from pathlib import Path

>>>>>>> 3ccf4fd (Committing all changes)


def print_schema_summary(matrix_path="output/schema_matrix.json"):
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)
    print("\n📊 Schema Dashboard")
    for site, data in matrix.get("sites", {}).items():
<<<<<<< HEAD
        score = data.get("score_summary", {}).get("field_score", "–")
        tags = ", ".join(data.get("domain_tags", []))
        print(f" - {site}: {score} points [{tags}]")
=======
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
            print(f"  • {item['site']}: {item['field_score']} pts, {item['plugin_count']} plugins")

    if export_path:
        Path(export_path).write_text(json.dumps(summary, indent=2))
        if verbose:
            print(f"\n[✓] Schema dashboard summary saved to {export_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schema Dashboard Stub")
    parser.add_argument("--matrix-path", required=True, help="Path to schema_matrix.json")
    parser.add_argument("--export-json", help="Output path for dashboard summary")
    parser.add_argument("--verbose", action="store_true", help="Verbose printout")
    args = parser.parse_args()

    summarize_sites(args.matrix_path, args.export_json, args.verbose)
>>>>>>> 3ccf4fd (Committing all changes)
