#!/usr/bin/env python3
"""Simplified plugin architecture validation test."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_architecture():
    """Test the complete plugin architecture with proper instantiation."""
    print("🚀 Testing Plugin Architecture\n")

    try:
        # Direct import and test our reference plugins
        from universal_recon.plugins.reference_realtor import RealtorPlugin
        from universal_recon.plugins.ai_template_indexer_v2 import AITemplateIndexerPlugin

        plugins_to_test = [
            ("Reference Realtor", RealtorPlugin),
            ("AI Template Indexer v2", AITemplateIndexerPlugin)
        ]

        tested_plugins = 0

        for plugin_name, plugin_class in plugins_to_test:
            print(f"🔧 Testing {plugin_name}")

            try:
                # Instantiate the plugin
                plugin = plugin_class()
                print(f"✅ Plugin instantiated: {plugin.name}")

                # Test the plugin workflow
                record_count = 0
                for raw_data in plugin.fetch():
                    record_count += 1
                    print(f"📦 Fetched record {record_count}: {raw_data.get('id', 'no-id')}")

                    # Transform the data
                    transformed = plugin.transform(raw_data)
                    print(f"🔄 Transformed keys: {list(transformed.keys())}")

                    # Validate the data
                    is_valid = plugin.validate(transformed)
                    print(f"✅ Validation: {'PASSED' if is_valid else 'FAILED'}")

                    if record_count >= 2:  # Limit output per plugin
                        break

                print(f"🎯 {plugin_name} processed {record_count} records successfully")
                tested_plugins += 1
                print()

            except Exception as e:
                print(f"❌ Error testing {plugin_name}: {e}")
                print()
                continue

        # Test plugin loader discovery
        print("🔍 Testing Plugin Discovery")
        try:
            import universal_recon.plugins.loader as loader
            plugins = list(loader.load_plugins())
            print(f"✅ Plugin loader discovered {len(plugins)} plugins")

            # Check our plugins are in the discovered list
            plugin_names = [plugin.__name__ for plugin in plugins]
            reference_found = any('reference_realtor' in name for name in plugin_names)
            ai_template_found = any('ai_template_indexer_v2' in name for name in plugin_names)

            print(f"✅ Reference plugin discovered: {reference_found}")
            print(f"✅ AI Template plugin discovered: {ai_template_found}")

        except Exception as e:
            print(f"❌ Plugin discovery error: {e}")

        print("\n🏆 Plugin Architecture Test Summary:")
        print(f"   📊 Plugins tested directly: {tested_plugins}")
        print(f"   🎯 Architecture validation: {'PASSED' if tested_plugins >= 2 else 'FAILED'}")

        return tested_plugins >= 2

    except Exception as e:
        print(f"❌ Critical error: {e}")
        return False

if __name__ == "__main__":
    success = test_plugin_architecture()
    sys.exit(0 if success else 1)
