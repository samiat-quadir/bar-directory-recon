import argparse
import json
import os
import sys

from core.retry import retry
from utils.output_manager import save_summary
from core.plugin_loader import load_plugins_by_type
from core.config_loader import ConfigManager
from analytics.site_schema_collector import run_site_schema_collection
from analytics.schema_score_linter import run_schema_score_lint
from validators.fieldmap_validator import validate_fieldmap
from plugin_aggregator import aggregate_and_print

def parse_args():
    parser = argparse.ArgumentParser(description="Universal Recon Tool CLI")
    parser.add_argument("--site", required=True, help="Target site slug (e.g., utah_bar)")
    parser.add_argument("--strict-schema", action="store_true", help="Enable strict schema validation")
    parser.add_argument("--verbose", action="store_true", help="Print detailed trace summaries")
    parser.add_argument("--full-report", action="store_true", help="Generate merged full_report.json")
    parser.add_argument("--recon-report", action="store_true", help="Enable recon_summary_builder output")
    parser.add_argument("--audit-report", action="store_true", help="Enable audit reporting")
    parser.add_argument("--trend-analysis", action="store_true", help="Run trend tracker")
    parser.add_argument("--audit-heatmap", action="store_true", help="Include heatmap in analytics")
    parser.add_argument("--heatmap-summary", action="store_true", help="Print heatmap trace summary")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving files")
    parser.add_argument("--schema-collect", action="store_true", help="Run the site schema collector and export fieldmap")
    parser.add_argument("--schema-lint", action="store_true", help="Run the fieldmap validator on the site fieldmap")
    parser.add_argument("--schema-score", action="store_true", help="Run fieldmap scoring to detect coverage issues")
    return parser.parse_args()

def load_normalized_records(site_name):
    input_path = os.path.abspath(f"output/normalized/{site_name}_normalized.json")
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [
            {"type": "email", "value": "jane@example.com", "plugin": "mock_plugin"},
            {"type": "bar_number", "value": "12345", "plugin": "mock_plugin"},
            {"type": "firm_name", "value": "Smith LLP", "plugin": "mock_plugin"}
        ]

def main():
    args = parse_args()
    site_name = args.site
    cli_flags = vars(args)
    config = ConfigManager().as_dict()

    if args.schema_collect:
        print("🔍 Running Site Schema Collector...")
        fieldmap = run_site_schema_collection(config={"site_name": site_name})
        if fieldmap:
            print("✅ Site schema fieldmap written.")
        else:
            print("⚠️ Schema collector returned no data.")

    if args.schema_lint:
        print("🧪 Validating fieldmap...")
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        validate_fieldmap(path, verbose=args.verbose)

    if args.schema_score:
        print("📏 Scoring fieldmap...")
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        run_schema_score_lint(path, verbose=args.verbose)

    if not args.full_report:
        return  # Skip the rest if full pipeline not requested

    records = load_normalized_records(site_name)
    validator_plugins = load_plugins_by_type("validator")
    validated_records = records
    for plugin in validator_plugins:
        if hasattr(plugin, "validate"):
            validated_records = plugin.validate(validated_records, config=config, strict=args.strict_schema)

    aggregate_and_print(
        records=validated_records,
        site_name=site_name,
        config=config,
        cli_flags=cli_flags
    )

if __name__ == "__main__":
    main()
    