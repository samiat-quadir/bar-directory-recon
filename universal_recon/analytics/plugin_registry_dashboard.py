# === analytics/plugin_registry_dashboard.py ===

import json
from pathlib import Path

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

