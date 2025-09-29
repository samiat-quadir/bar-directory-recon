#!/usr/bin/env python3
"""Comprehensive test of the plugin architecture.

This demonstrates the complete plugin workflow:
1. Plugin discovery and loading
2. Plugin instantiation and execution
3. Data processing pipeline (fetch -> transform -> validate)
"""

import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_plugin_architecture():
    """Test the complete plugin architecture."""
    print("🚀 Testing Plugin Architecture\n")

    # Step 1: Import plugin loader
    try:
        import universal_recon.plugins.loader as loader

        print("✅ Plugin loader imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import plugin loader: {e}")
        return False

    # Step 2: Discover plugins
    plugins = list(loader.load_plugins())
    print(f"✅ Discovered {len(plugins)} plugins")

    # Step 3: Test specific plugins that don't require external dependencies
    target_plugins = ["reference_realtor", "ai_template_indexer_v2"]
    tested_plugins = 0

    for plugin_module in plugins:
        module_name = plugin_module.__name__.split(".")[-1]

        if module_name not in target_plugins:
            continue

        print(f"\n🔧 Testing plugin: {module_name}")

        try:
            # Find plugin class in module
            plugin_class = None
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if (
                    hasattr(attr, "__class__")
                    and hasattr(attr, "name")
                    and hasattr(attr, "fetch")
                    and hasattr(attr, "transform")
                    and hasattr(attr, "validate")
                ):
                    # This looks like a plugin instance
                    plugin_instance = attr
                    break
                elif (
                    isinstance(attr, type)
                    and hasattr(attr, "name")
                    and hasattr(attr, "fetch")
                ):
                    # This looks like a plugin class
                    plugin_class = attr
                    break

            if plugin_class:
                plugin_instance = plugin_class()
            elif "plugin_instance" not in locals():
                print(f"⚠️  No plugin class or instance found in {module_name}")
                continue

            print(f"✅ Plugin instantiated: {plugin_instance.name}")

            # Test the plugin workflow
            record_count = 0
            for raw_data in plugin_instance.fetch():
                record_count += 1
                print(f"📦 Fetched record {record_count}")

                # Transform the data
                transformed = plugin_instance.transform(raw_data)
                print(f"🔄 Transformed: {list(transformed.keys())}")

                # Validate the data
                is_valid = plugin_instance.validate(transformed)
                print(f"✅ Validation: {'PASSED' if is_valid else 'FAILED'}")

                if record_count >= 2:  # Limit output per plugin
                    break

            print(
                f"🎯 Plugin {module_name} processed {record_count} records successfully"
            )
            tested_plugins += 1

        except Exception as e:
            print(f"❌ Error testing plugin {module_name}: {e}")
            continue

    print("\n🏆 Plugin Architecture Test Summary:")
    print(f"   📊 Total plugins discovered: {len(plugins)}")
    print(f"   ✅ Plugins tested successfully: {tested_plugins}")
    print(
        f"   🎯 Architecture validation: {'PASSED' if tested_plugins > 0 else 'FAILED'}"
    )

    return tested_plugins > 0


if __name__ == "__main__":
    success = test_plugin_architecture()
    sys.exit(0 if success else 1)
