# === universal_recon/main.py ===

import argparse
import os
from datetime import datetime
from analytics.schema_matrix_collector import collect_schema_matrix, write_schema_matrix
from core.config_loader import ConfigManager
from plugin_loader import load_normalized_records
from plugin_aggregator import aggregate_and_print

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--schema-collect", action="store_true")
    parser.add_argument("--schema-lint", action="store_true")
    parser.add_argument("--domain-lint", action="store_true")
    parser.add_argument("--schema-score", action="store_true")
    parser.add_argument("--schema-matrix", action="store_true")
    parser.add_argument("--full-report", action="store_true")
    parser.add_argument("--score-drift", action="store_true")
    parser.add_argument("--dashboard", action="store_true", help="Run the schema trend dashboard overlay.")
    parser.add_argument("--drift-overlay", action="store_true", help="Run the drift matrix overlay.")
    parser.add_argument("--plugin-decay", action="store_true", help="Run plugin decay analysis.")
    parser.add_argument("--plugin-diff", action="store_true", help="Run plugin usage diff analysis.")
    parser.add_argument("--validator-overlay", action="store_true", help="Run validator drift overlay.")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    site_name = args.site

    os.makedirs("output/fieldmap", exist_ok=True)

    if args.schema_collect:
        from analytics.site_schema_collector import run_site_schema_collection
        run_site_schema_collection(site_name, verbose=args.verbose)

    if args.schema_lint:
        from validators.fieldmap_validator import run_fieldmap_validator
        run_fieldmap_validator(site_name, verbose=args.verbose)

    if args.schema_score:
        from analytics.schema_score_linter import run_schema_score_lint
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        run_schema_score_lint(path, verbose=args.verbose)

    if args.domain_lint:
        from validators.fieldmap_domain_linter import domain_lint_fieldmap
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        domain_lint_fieldmap(path, verbose=args.verbose)

    if args.schema_matrix:
        matrix = collect_schema_matrix(
            fieldmap_dir="output/fieldmap",
            plugin_dir="output/plugins"
        )
        save_path = "output/schema_matrix.json"
        write_schema_matrix(matrix, save_path, verbose=args.verbose)


    if args.full_report:
        records = load_normalized_records(site_name)
        config = ConfigManager().as_dict()
        cli_flags = vars(args)
        aggregate_and_print(records, site_name, config, cli_flags)

    if args.score_drift:
        from analytics.score_drift_export import generate_drift_csv
        generate_drift_csv(site=args.site)

    if args.dashboard:
        from analytics.trend_overlay_dashboard import run_trend_overlay_dashboard
        run_trend_overlay_dashboard()

    if args.drift_overlay:
        from analytics.drift_matrix_overlay import run_drift_overlay
        run_drift_overlay()

    if args.plugin_decay:
        from analytics.plugin_decay_overlay import run_plugin_decay_overlay
        run_plugin_decay_overlay()

    if args.plugin_diff:
        from analytics.plugin_usage_diff import run_plugin_usage_diff
        run_plugin_usage_diff()

    if args.validator_overlay:
        from analytics.validator_drift_overlay import run_validator_drift_overlay
        run_validator_drift_overlay()

if __name__ == "__main__":
    main()
