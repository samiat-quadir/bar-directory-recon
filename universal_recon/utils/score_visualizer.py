import collections
import json
from typing import List, Dict


def generate_heatmap_data(records: List[Dict]) -> Dict:
    """
    Generates a tiered error heatmap based on score tiers and plugin field sources.
    :param records: List of ADA-schema validated records with 'plugin', 'type', 'score'
    :return: Nested dictionary: plugin → field type → score tier → count
    """
    heatmap = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    for record in records:
        plugin = record.get("plugin", "unknown_plugin")
        field_type = record.get("type", "unknown_field")
        score = record.get("score", 0)
        tier = (
            "critical" if score <= 2
            else "warning" if score <= 4
            else "clean"
        )
        heatmap[plugin][field_type][tier] += 1

    return {
        plugin: {
            field: dict(counts)
            for field, counts in fields.items()
        }
        for plugin, fields in heatmap.items()
    }


def save_heatmap_data(site_name: str, heatmap_data: Dict):
    """
    Saves heatmap JSON output to output/reports/{site}_heatmap.json
    """
    path = f"output/reports/{site_name}_heatmap.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(heatmap_data, f, indent=2)


def print_top_heatmap_errors(heatmap_data: Dict, top_n: int = 3):
    """
    Prints the top plugin-field error combinations by total (critical + warning).
    """
    error_counts = []
    for plugin, fields in heatmap_data.items():
        for field, tiers in fields.items():
            crit = tiers.get("critical", 0)
            warn = tiers.get("warning", 0)
            if crit > 0 or warn > 0:
                total = crit + warn
                error_counts.append((total, plugin, field, crit, warn))

    top_errors = sorted(error_counts, reverse=True)[:top_n]
    if top_errors:
        print("📊 Top Plugin-Field Errors (Critical + Warning):")
        for _, plugin, field, crit, warn in top_errors:
            print(f"  • [{plugin}] {field} → ⚠️ {warn} | 🔴 {crit}")


def get_top_plugin_field_errors(heatmap_data: Dict, top_n: int = 5) -> List[Dict]:
    """
    Returns a list of the top plugin-field errors for external use or testing.
    """
    results = []
    for plugin, fields in heatmap_data.items():
        for field, tiers in fields.items():
            crit = tiers.get("critical", 0)
            warn = tiers.get("warning", 0)
            total = crit + warn
            if total > 0:
                results.append({
                    "plugin": plugin,
                    "field": field,
                    "critical": crit,
                    "warning": warn,
                    "total": total
                })
    return sorted(results, key=lambda x: x["total"], reverse=True)[:top_n]
