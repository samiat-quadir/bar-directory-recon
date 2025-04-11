import argparse
import sys
import os
import json

from plugin_loader import load_plugins_by_type
from plugin_aggregator import aggregate_and_print
from analytics.site_schema_collector import run_site_schema_collection
from validators.fieldmap_validator import validate_fieldmap

def main():
    parser = argparse.ArgumentParser(description="Universal Recon Tool")

    parser.add_argument('--site', type=str, required=True, help='Site name for config and output routing')
    parser.add_argument('--config', type=str, default="config/config.json", help='Path to config file')
    parser.add_argument('--full-report', action='store_true', help='Generate full report with all modules')
    parser.add_argument('--print-report', action='store_true', help='Print output summary to terminal')
    parser.add_argument('--schema-collect', action='store_true', help='Run the site schema collector and export fieldmap')
    parser.add_argument('--schema-lint', action='store_true', help='Run fieldmap validator on exported schema')
    parser.add_argument('--verbose', action='store_true', help='Print additional diagnostic output')
    parser.add_argument('--run-mode', type=str, default="full", choices=["lite", "full"], help='Plugin run mode (lite or full)')

    args = parser.parse_args()

    # Load config
    if not os.path.exists(args.config):
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    site_name = args.site
    cli_flags = sys.argv[1:]

    # ✅ Schema collection
    if args.schema_collect:
        print("🔍 Running Site Schema Collector...")
        fieldmap = run_site_schema_collection(config=config)
        if fieldmap:
            print("✅ Site schema fieldmap written.")
        else:
            print("⚠️ Schema collector returned no data.")
        if not args.full_report:
            sys.exit(0)

    # ✅ Optional schema linting
    if args.schema_lint:
        print("🧪 Running Fieldmap Validator...")
        fieldmap_path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
        result = validate_fieldmap(fieldmap_path, verbose=args.verbose)
        if result:
            print(json.dumps(result, indent=2))
        if not args.full_report:
            sys.exit(0)

    # Mocked example for validated records
    validated_records = [{"name": "John Doe", "email": "john@example.com"}]

    aggregate_and_print(validated_records, site_name, config, cli_flags)

if __name__ == "__main__":
    main()
