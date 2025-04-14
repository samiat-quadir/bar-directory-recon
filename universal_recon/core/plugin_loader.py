import importlib
import json
import os
import sys
from pathlib import Path


def load_plugins_by_type(plugin_type: str):
    """
    Loads all plugins from the registry of the specified type (e.g., validator, analytics).
    """
    plugins = []
    root = Path(__file__).resolve().parent
    registry_path = os.path.join(root, "plugin_registry.json")

    if not os.path.exists(registry_path):
        print(f"❌ Plugin registry not found: {registry_path}")
        return []

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load plugin registry: {e}")
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
