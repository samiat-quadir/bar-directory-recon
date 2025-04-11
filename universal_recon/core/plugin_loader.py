import json
import importlib
import os
from typing import List, Optional


def load_plugins_by_type(
    plugin_type: str,
    run_mode: Optional[str] = None,
    required_flags: Optional[List[str]] = None,
    registry_path: str = "plugin_registry.json"
):
    """
    Loads plugins of a given type, optionally filtered by run_mode or CLI flags.

    Args:
        plugin_type (str): e.g., 'analytics', 'validator'
        run_mode (str, optional): 'lite', 'full', etc.
        required_flags (List[str], optional): CLI flags that must match for plugin inclusion
        registry_path (str): path to plugin_registry.json

    Returns:
        List: Loaded plugin modules
    """
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load plugin registry: {e}")
        return []

    plugins = []

    for plugin in registry:
        if plugin.get("type") != plugin_type:
            continue

        # Optional run mode check
        if run_mode and plugin.get("run_mode") not in (None, run_mode, "all"):
            continue

        # Optional CLI flag match check
        if required_flags:
            plugin_flags = plugin.get("cli_flags", [])
            if not any(flag in plugin_flags for flag in required_flags):
                continue

        module_path = plugin.get("module")
        try:
            plugin_module = importlib.import_module(module_path)
            plugins.append(plugin_module)
        except Exception as e:
            print(f"[WARN] Failed to load plugin: {module_path} → {e}")

    return plugins

def get_plugin_metadata(registry_path: str = "plugin_registry.json") -> List[dict]:
    """
    Loads and returns the raw plugin metadata from the registry.

    Returns:
        List[dict]: Plugin entries including type, module, run_mode, cli_flags, etc.
    """
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read plugin registry: {e}")
        return []