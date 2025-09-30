"""Visualization generation for validation scores."""

import json
import os

from universal_recon.core.logger import get_logger

logger = get_logger(__name__)


def generate_heatmap_data(records: list[dict]) -> dict:
    """Generate heatmap data from validation records."""
    heatmap = {}
    for record in records:
        plugin = record.get("plugin", "unknown")
        record_type = record.get("type", "unknown")
        score = record.get("score", 0)

        if plugin not in heatmap:
            heatmap[plugin] = {}
        if record_type not in heatmap[plugin]:
            heatmap[plugin][record_type] = {"critical": 0, "warning": 0, "clean": 0}

        if score < 2:
            heatmap[plugin][record_type]["critical"] += 1
        elif score < 4:
            heatmap[plugin][record_type]["warning"] += 1
        else:
            heatmap[plugin][record_type]["clean"] += 1

    return heatmap


def save_heatmap_data(site: str, heatmap: dict) -> None:
    """Save heatmap data to JSON file."""
    os.makedirs("output/reports", exist_ok=True)
    output_path = f"output/reports/{site}_heatmap.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(heatmap, f, indent=2)


def generate_visualization(records: list[dict], site: str) -> dict:
    """Generate visualization from validation records."""
    try:
        heatmap = generate_heatmap_data(records)
        save_heatmap_data(site, heatmap)
        return heatmap
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        return {}
