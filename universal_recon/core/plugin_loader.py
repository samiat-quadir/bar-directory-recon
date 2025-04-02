import importlib
import json
import os

def load_plugins(registry_path="plugin_registry.json", plugin_type=None):
    if not os.path.exists(registry_path):
        print("❌ Plugin registry not found.")
        return []

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    loaded_plugins = []
    for entry in registry:
        if plugin_type and entry.get("type") != plugin_type:
            continue
        if not entry.get("enabled", False):
            continue
        try:
            module_path = entry["module"]
            mod = importlib.import_module(module_path)
            loaded_plugins.append((entry["name"], mod))
        except ImportError as e:
            print(f"⚠️ Could not load plugin {entry['name']}: {e}")
    return loaded_plugins