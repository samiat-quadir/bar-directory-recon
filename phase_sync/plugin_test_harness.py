import sys
import os
import json

# Adjust these imports if your 'core/' folder is at a different relative path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.plugin_loader import load_plugins
from core.report_printer import print_full_report
# from core.retry import retry  # use if you want to demonstrate retry on certain calls

def main():
    print("=== PHASE 14B: PLUGIN TEST HARNESS ===")

    # 1. Path to plugin registry
    registry_path = os.path.join(os.path.dirname(__file__), 'plugin_registry.json')
    if not os.path.exists(registry_path):
        print(f"❌ plugin_registry.json not found at {registry_path}")
        return

    # 2. Load plugins
    plugins = load_plugins(registry_path=registry_path, plugin_type=None)
    print(f"Loaded {len(plugins)} plugin(s):")
    for (name, mod) in plugins:
        print(f" - {name} => {mod}")

    # 3. Example calls to each plugin's main function
    for (name, mod) in plugins:
        # Attempt a 'run_analysis' or 'validate' or 'main' function
        # Adjust based on your plugin methods
        if hasattr(mod, 'run_analysis'):
            try:
                print(f"\n[Plugin: {name}] -> run_analysis()")
                analysis_result = mod.run_analysis()  # or pass in test data if needed
                print(f"Analysis result: {analysis_result}")
            except Exception as e:
                print(f"Error running run_analysis on {name}: {e}")

        elif hasattr(mod, 'validate'):
            try:
                print(f"\n[Plugin: {name}] -> validate()")
                # Provide minimal test data
                sample_data = {"field": "test_value"}
                validation_result = mod.validate(sample_data)
                print(f"Validation result: {validation_result}")
            except Exception as e:
                print(f"Error running validate on {name}: {e}")
        else:
            print(f"\n[Plugin: {name}] has no recognized entry function (run_analysis/validate). Skipping.")

    # 4. Attempt to print a consolidated report from output/ (if available)
    site_name = "test_site"
    print("\n=== Attempting to load & print full report (summary, audit, trend) ===")
    # If your site-based outputs are named differently, adjust accordingly
    print_full_report(site_name)

    print("\n=== Test Harness Completed ===")

if __name__ == "__main__":
    main()