# === analytics/plugin_registry_dashboard.py ===

<<<<<<< HEAD
import json


def summarize_plugin_coverage(matrix_path="output/schema_matrix.json"):
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)
    plugins_by_site = {}
    for site, data in matrix.get("sites", {}).items():
        plugins = data.get("plugins_used", [])
        for p in plugins:
            plugins_by_site.setdefault(p, []).append(site)
    print("\n🔌 Plugin Usage Summary")
    for plugin, sites in plugins_by_site.items():
        print(f" - {plugin}: used in {len(sites)} site(s)")
=======
import argparse
import json
from collections import Counter
from pathlib import Path


def analyze_plugins(matrix_path: str, export_path: str = None, verbose: bool = False):
    matrix = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    plugin_counter = Counter()

    for site_data in matrix.get("sites", {}).values():
        for plugin in site_data.get("plugins_used", []):
            plugin_counter[plugin] += 1

    if verbose:
        print("\n🔍 Plugin Usage Summary:")
        for plugin, count in plugin_counter.most_common():
            print(f"  • {plugin}: {count} site(s)")

    if export_path:
        output_data = {
            "plugin_summary": dict(plugin_counter),
            "site_count": len(matrix.get("sites", {})),
            "source": matrix_path,
        }
        Path(export_path).write_text(json.dumps(output_data, indent=2))
        if verbose:
            print(f"\n[✓] Plugin registry dashboard saved to {export_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plugin Registry Dashboard")
    parser.add_argument("--matrix-path", required=True, help="Path to schema_matrix.json")
    parser.add_argument("--export-json", help="Path to export JSON plugin summary")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    analyze_plugins(args.matrix_path, args.export_json, args.verbose)
>>>>>>> 3ccf4fd (Committing all changes)
