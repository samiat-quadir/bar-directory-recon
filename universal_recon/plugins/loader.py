"""Plugin loader utility for dynamic plugin discovery and loading.

This module provides functionality to automatically discover and load
all plugins in the universal_recon.plugins package.
"""

import importlib
import pkgutil
from collections.abc import Iterator
from typing import Any


def load_plugins() -> Iterator[Any]:
    """Dynamically discover and load all plugins from the plugins package.

    Yields:
        Any: Loaded plugin modules that implement the Plugin protocol
    """
    import universal_recon.plugins as plugins_package

    # Iterate through all modules in the plugins package
    for importer, modname, ispkg in pkgutil.iter_modules(plugins_package.__path__):
        # Skip the base protocol and loader itself
        if modname in ("base", "loader"):
            continue

        # Import the module
        full_module_name = f"universal_recon.plugins.{modname}"
        try:
            module = importlib.import_module(full_module_name)
            yield module
        except ImportError as e:
            print(f"Warning: Failed to import plugin {full_module_name}: {e}")
            continue
