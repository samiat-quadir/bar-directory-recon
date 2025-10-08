#!/usr/bin/env python3
"""
Plugin Registry Validator - Non-blocking CI diagnostic
Validates plugin_registry.json against schema if present.
"""
import json
import sys
from pathlib import Path


def load_schema():
    """Load the JSON schema for plugin registry."""
    schema_path = Path(__file__).parent / "schemas" / "plugin_registry.schema.json"
    if not schema_path.exists():
        return None
    return json.loads(schema_path.read_text(encoding="utf-8"))


def load_registry():
    """Load plugin_registry.json if it exists."""
    registry_path = Path("plugin_registry.json")
    if not registry_path.exists():
        return None
    try:
        return json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}


def validate_basic_structure(registry):
    """Basic validation without jsonschema library."""
    issues = []

    if "error" in registry:
        issues.append(f"❌ {registry['error']}")
        return issues

    if not isinstance(registry, dict):
        issues.append("❌ Registry must be a JSON object")
        return issues

    if "plugins" not in registry:
        issues.append("❌ Missing required field: 'plugins'")

    if "version" not in registry:
        issues.append("❌ Missing required field: 'version'")

    if "plugins" in registry:
        if not isinstance(registry["plugins"], list):
            issues.append("❌ 'plugins' must be an array")
        else:
            for i, plugin in enumerate(registry["plugins"]):
                if not isinstance(plugin, dict):
                    issues.append(f"❌ Plugin {i}: must be an object")
                    continue

                for required_field in ["name", "version", "entry_point"]:
                    if required_field not in plugin:
                        issues.append(
                            f"❌ Plugin {i} ({plugin.get('name', '?')}): missing '{required_field}'"
                        )

    return issues


def main():
    print("🔍 Plugin Registry Validator")
    print("=" * 60)

    registry = load_registry()

    if registry is None:
        print("ℹ️  No plugin_registry.json found - skipping validation")
        sys.exit(0)

    issues = validate_basic_structure(registry)

    if issues:
        print("\n".join(issues))
        print(f"\n❌ FAIL: {len(issues)} issue(s) detected")
    else:
        plugin_count = len(registry.get("plugins", []))
        print(f"✅ PASS: plugin_registry.json is valid")
        print(f"✅ {plugin_count} plugin(s) registered")

    # Non-blocking: always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
