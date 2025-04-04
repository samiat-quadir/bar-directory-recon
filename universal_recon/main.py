import argparse
import json
import os

from utils.retry import retry
from utils.output_manager import save_summary
from core.plugin_loader import load_plugins_by_type
from validators.record_field_validator_v3 import validate_records
from analytics.plugin_aggregator import aggregate_and_print


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
    return parser.parse_args()


def load_normalized_records(site_name):
    # For this demo, mock normalized records
    input_path = f"output/normalized/{site_name}_normalized.json"
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Mock fallback
        return [
            {"type": "email", "value": "jane@example.com", "plugin": "mock_plugin"},
            {"type": "bar_number", "value": "12345", "plugin": "mock_plugin"},
            {"type": "firm_name", "value": "Smith LLP", "plugin": "mock_plugin"}
        ]


def main():
    args = parse_args()
    site_name = args.site
    cli_flags = vars(args)

    # Load config (stub for now)
    config = {"validation": {"strict": args.strict_schema}}

    # Step 1: Load normalized records
    records = load_normalized_records(site_name)

    # Step 2: Run all validator plugins (from registry)
    validator_plugins = load_plugins_by_type("validator")
    validated_records = records
    for plugin in validator_plugins:
        if hasattr(plugin, "validate"):
            validated_records = plugin.validate(validated_records, config=config, strict=args.strict_schema)

    # Step 3: Pass to aggregator → run all analytics + print CLI summary
    aggregate_and_print(
        records=validated_records,
        site_name=site_name,
        config=config,
        cli_flags=cli_flags
    )


if __name__ == "__main__":
    main()
