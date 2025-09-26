# universal_recon/plugin_loader.py

import importlib
import json
import os
from pathlib import Path
from typing import Any


def load_plugins_by_type(plugin_type: str) -> list[Any]:
    plugins = []
    root = Path(__file__).resolve().parent
    registry_path = os.path.join(root, "plugin_registry.json")

    if not os.path.exists(registry_path):
        print(f"❌ Plugin registry not found: {registry_path}")
        return []

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in plugin registry: {registry_path}")
        return []

    for entry in registry:
        if entry.get("type") == plugin_type:
            module_path = entry.get("module")
            try:
                plugin = importlib.import_module(module_path)
                plugins.append(plugin)
            except Exception as e:
                print(f"[WARN] Failed to load plugin: {module_path} → {e}")

    return plugins


def load_normalized_records(site_name: str) -> list[dict[str, Any]]:
    path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in fieldmap: {path}")
        return []

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "records" in data:
            return data["records"]
        elif "fields" in data and "score_summary" in data:
            return [{"plugin": "aggregated_fieldmap", **data}]
        elif "fields" in data:
            # Handle single fieldmap record (no score_summary)
            return [data]
        else:
            # Fallback: try to unpack dict of dicts
            return [{"plugin": key, **val} for key, val in data.items() if isinstance(val, dict)]
    else:
        raise ValueError(f"Unsupported fieldmap structure in {path}")
