# main.py
# Phase 18b+ CLI – Last updated: April 11, 2025

import argparse
import json
import os
import sys
from pathlib import Path

# Dynamically resolve internal paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "core"))

# Import core modules
from core.plugin_loader import load_plugins_by_type
from plugin_aggregator import aggregate_and_print
from analytics.site_schema_collector import run_site_schema_collection
from validators.fieldmap_validator import validate_fieldmap

def parse_args():
    parser = argparse.ArgumentParser(description="Universal Recon Tool CLI")
    parser.add_argument("--site", required=True, help="Target site slug (e.g., utah_bar)")
    parser.add_argument("--config", default="config/config.json", help="Path to config file")
    parser.add_argument("--schema-collect", action="store_true", help="Run site schema collector")
    parser.add_argument("--schema-lint", action="store_true", help="Run fieldmap validator")
    parser.add_argument("--verbose", action="store_true", help="Print extra diagnostics")
    parser.add_argument("--full-report", action="store_true", help="Enable full report generation")
    parser.add_argument("--print-report", action="store_true", help="Print report output to CLI")
    parser.add_argument("--run-mode", default="full", choices=["lite", "full"], help="Plugin mode selector")
    return parser.parse_args()

def load_config(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"❌ Config not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_normalized_records(site_name):
    path = os.path.join(ROOT, "output", "normalized", f"{site_name}_normalized.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"type": "email", "value": "jane@example.com", "plugin": "mock_plugin"},
        {"type": "bar_number", "value": "12345", "plugin": "mock_plugin"},
        {"type": "firm_name", "value": "Smith LLP", "plugin": "mock_plugin"}
    ]

def main():
    args = parse_args()
    config = load_config(args.config)
    site = args.site
    cli_flags = vars(args)

    # === Step 1: Schema Collection ===
    if args.schema_collect:
        print("🔍 Running Site Schema Collector...")
        fieldmap = run_site_schema_collection(config=config)
        print("✅ Fieldmap written." if fieldmap else "⚠️ No fieldmap returned.")
        if not args.full_report:
            return

    # === Step 2: Fieldmap Validation ===
    if args.schema_lint:
        print("🧪 Running Fieldmap Validator...")
        path = os.path.join(ROOT, "output", "fieldmap", f"{site}_fieldmap.json")
        result = validate_fieldmap(path, verbose=args.verbose)
        if result and args.verbose:
            print(json.dumps(result, indent=2))
        if not args.full_report:
            return

    # === Step 3: Load Records & Run Aggregator ===
    validated_records = load_normalized_records(site)
    aggregate_and_print(validated_records, site, config, cli_flags)

if __name__ == "__main__":
    main()
