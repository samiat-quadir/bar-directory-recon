import json
import importlib
import os


def load_plugins_by_type(plugin_type: str, registry_path: str = "plugin_registry.json"):
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    plugins = []
    for plugin in registry:
        if plugin.get("type") == plugin_type:
            module_path = plugin.get("module")
            try:
                plugin_module = importlib.import_module(module_path)
                plugins.append(plugin_module)
            except Exception as e:
                print(f"[WARN] Failed to load plugin: {module_path} → {e}")

    return plugins
