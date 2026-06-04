#!/usr/bin/env python3
"""Test the converted AI Template Indexer plugin."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from universal_recon.plugins.ai_template_indexer_v2 import AITemplateIndexerPlugin
    print("✅ AI Template Indexer plugin imported successfully")

    # Create plugin instance
    plugin = AITemplateIndexerPlugin()
    print(f"✅ Plugin instantiated: {plugin.name}")

    # Test fetch method
    fetch_count = 0
    for record in plugin.fetch():
        fetch_count += 1
        print(f"📦 Fetched record {fetch_count}: {record.get('group_id', 'unknown')}")

        # Test transform method
        transformed = plugin.transform(record)
        print(f"🔄 Transformed to type: {transformed['template_type']} (confidence: {transformed['template_confidence']})")

        # Test validate method
        is_valid = plugin.validate(transformed)
        print(f"✅ Validation: {'PASSED' if is_valid else 'FAILED'}")
        print()

        if fetch_count >= 3:  # Limit output
            break

    print(f"🎯 AI Template Indexer plugin test COMPLETED - processed {fetch_count} records")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Plugin test error: {e}")
    sys.exit(1)
