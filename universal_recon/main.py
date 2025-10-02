# universal_recon/main.py

import argparse

from universal_recon.core.multisite_config_manager import ConfigManager
from universal_recon.core.snapshot_manager import SnapshotArchiver
from universal_recon.plugin_loader import load_normalized_records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--schema-collect", action="store_true")
    parser.add_argument("--schema-lint", action="store_true")
    parser.add_argument("--domain-lint", action="store_true")
    parser.add_argument("--schema-score", action="store_true")
    parser.add_argument("--schema-matrix", action="store_true")
    parser.add_argument("--plugin-diff", action="store_true")
    parser.add_argument("--score-drift", action="store_true")
    parser.add_argument("--plugin-decay", action="store_true")
    parser.add_argument("--full-report", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--emit-status",
        action="store_true",
        help="Emit site health and validator drift status",
    )
    parser.add_argument(
        "--emit-drift-dashboard",
        action="store_true",
        help="generate drift dashboard HTML",
    )
    parser.add_argument(
        "--emit-risk-overlay",
        action="store_true",
        help="emit risk_overlay.json using validator tiers",
    )
    # Realtor directory automation arguments
    parser.add_argument("--output", help="Output file path for realtor directory scraping")
    parser.add_argument("--max-records", type=int, help="Maximum number of records to scrape")
    parser.add_argument("--google-sheet-id", help="Google Sheets ID for upload")
    args = parser.parse_args()

    site_name = args.site

    # Handle realtor directory scraping
    if site_name == "realtor_directory":
        from universal_recon.plugins.realtor_directory_plugin import (
            scrape_realtor_directory,
        )

        result = scrape_realtor_directory(
            output_path=args.output,
            max_records=args.max_records,
            google_sheet_id=args.google_sheet_id,
            verbose=args.verbose,
        )

        if result["success"]:
            print(f"✅ Successfully scraped {result['leads_count']} leads")
            if args.output:
                print(f"📄 Results saved to: {result['output_path']}")
        else:
            print(f"❌ Scraping failed: {result['error']}")

        return

    if args.schema_collect:
        from universal_recon.analytics.site_schema_collector import collect_fieldmap

        collect_fieldmap(site_name=site_name, verbose=args.verbose)

    if args.schema_lint:
        from universal_recon.analytics.schema_score_linter import run_schema_score_lint

        run_schema_score_lint(site_name)

    if args.domain_lint:
        from universal_recon.analytics.domain_anomaly_flagger import run_domain_linter

        run_domain_linter(site_name)

    if args.schema_score:
        from universal_recon.analytics.schema_score_linter import run_schema_score_lint

        run_schema_score_lint(site_name)

    if args.schema_matrix:
        from universal_recon.analytics.schema_matrix_collector import (
            collect_schema_matrix,
            save_schema_matrix,
        )

        matrix = collect_schema_matrix(fieldmap_dir="output/fieldmap", plugin_dir="output/plugins")
        save_schema_matrix(matrix)
        if args.verbose:
            print("✅ Schema matrix collected and saved.")
        archiver = SnapshotArchiver()
        archiver.archive_latest_matrix()

    if args.full_report:
        from universal_recon.plugin_aggregator import aggregate_and_print

        config = ConfigManager().as_dict()
        records = load_normalized_records(site_name)
        cli_flags = vars(args)
        aggregate_and_print(records, site_name, config, cli_flags)

    if args.plugin_diff:
        from universal_recon.analytics.plugin_usage_diff import smart_plugin_diff_runner

        smart_plugin_diff_runner(site=site_name)

    if args.score_drift:
        from universal_recon.analytics.score_drift_export import generate_drift_csv

        generate_drift_csv(site=site_name)

    if args.plugin_decay:
        from universal_recon.analytics.plugin_decay_overlay import (
            run_plugin_decay_overlay,
        )

        run_plugin_decay_overlay(site=site_name)

    if args.emit_status:
        from universal_recon.utils.status_summary_emitter import emit_status

        emit_status(verbose=args.verbose)

    if args.emit_drift_dashboard:
        from universal_recon.analytics.drift_dashboard_generator import (
            generate_dashboard,
        )

        generate_dashboard(site_name)

    if args.emit_risk_overlay:
        from universal_recon.analytics.risk_overlay_emitter import emit_site_risk_json

        emit_site_risk_json(site_name)


if __name__ == "__main__":
    main()
