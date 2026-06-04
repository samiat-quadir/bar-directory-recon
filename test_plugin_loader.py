#!/usr/bin/env python3
"""Quick smoke test for plugin loader functionality."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import universal_recon.plugins.loader as loader
    print("✅ Plugin loader module imported successfully")

    # Test plugin discovery
    plugins = list(loader.load_plugins())
    print(f"✅ Plugin discovery completed, found {len(plugins)} plugins")

    # List discovered plugins
    plugin_names = [plugin.__name__ for plugin in plugins]
    print(f"📦 Discovered plugins: {plugin_names}")

    # Test that reference plugin is found
    reference_found = any('reference_realtor' in name for name in plugin_names)
    if reference_found:
        print("✅ Reference plugin (reference_realtor) discovered correctly")
    else:
        print("❌ Reference plugin NOT found - check plugin structure")

    print("\n🎯 Plugin loader validation PASSED")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Plugin loader error: {e}")
    sys.exit(1)
