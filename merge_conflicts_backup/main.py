# === universal_recon/main.py ===

import argparse

<<<<<<< HEAD
import os

from analytics.schema_matrix_collector import collect_schema_matrix, save_schema_matrix
from core.config_loader import ConfigManager
from plugin_aggregator import aggregate_and_print
from plugin_loader import load_normalized_records

=======

<<<<<<< HEAD
from universal_recon.core.config_loader import ConfigManager
from universal_recon.core.snapshot_manager import SnapshotArchiver
from universal_recon.plugin_loader import load_normalized_records, load_plugins_by_type

>>>>>>> 3ccf4fd (Committing all changes)


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
    parser.add_argument("--plugin-diff", action="store_true")
    parser.add_argument("--verbose", action="store_true")
<<<<<<< HEAD
=======
    parser.add_argument("--emit-status", action="store_true", help="Emit site health and validator drift status")
=======
import os
import sys


def main():
"""TODO: Add docstring."""
    parser = argparse.ArgumentParser(description="Universal Recon CLI")

    # Core flags
    parser.add_argument("--site", help="Site name or config key.")
    parser.add_argument("--schema-collect", action="store_true", help="Collect fieldmap data.")
    parser.add_argument("--schema-lint", action="store_true", help="Validate fieldmap structure.")
    parser.add_argument("--schema-score", action="store_true", help="Score fieldmap completeness.")
    parser.add_argument("--domain-lint", action="store_true", help="Apply domain-based checks.")
    parser.add_argument("--schema-matrix", action="store_true", help="Build multi-site schema matrix.")
    parser.add_argument("--full-report", action="store_true", help="Aggregator merges full reports.")
    parser.add_argument("--verbose", action="store_true", help="Print verbose logs.")

    # Phase 20b analytics flags
    parser.add_argument("--dashboard", action="store_true", help="Show schema trend dashboard.")
    parser.add_argument("--drift-check", action="store_true", help="Track score drift across schema matrices.")
    parser.add_argument("--plugin-overlay", action="store_true", help="Show plugin usage overlay.")
    parser.add_argument("--export-csv", action="store_true", help="Export schema matrix to CSVs.")
    parser.add_argument("--export-html", action="store_true", help="Generate HTML overlay dashboard from schema_matrix.json")
    parser.add_argument("--heatmap-plugin", action="store_true", help="Render plugin usage heatmap.")
    parser.add_argument("--heatmap-drift", action="store_true", help="Render field score drift heatmap.")

>>>>>>> 54c6ae3 (Committing all changes)
    args = parser.parse_args()
>>>>>>> 3ccf4fd (Committing all changes)

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
<<<<<<< HEAD
        matrix = collect_schema_matrix(fieldmap_dir="output/fieldmap", plugin_dir="output/plugins")
        save_schema_matrix(matrix, path="output/schema_matrix.json")
=======
<<<<<<< HEAD
        from universal_recon.analytics.schema_matrix_collector import collect_schema_matrix, save_schema_matrix
        matrix = collect_schema_matrix(
            fieldmap_dir="output/fieldmap", plugin_dir="output/plugins"
        )
        save_schema_matrix(matrix)
=======
        import shutil
        from datetime import datetime

        from analytics.schema_matrix_collector import collect_schema_matrix, write_schema_matrix
    matrix_path = "output/schema_matrix.json"
    archive_dir = "output/archive"
    os.makedirs(archive_dir, exist_ok=True)

    # Archive existing matrix if it exists
    if os.path.exists(matrix_path):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archived_path = os.path.join(archive_dir, f"schema_matrix_{timestamp}.json")
        shutil.copy(matrix_path, archived_path)
>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)
        if args.verbose:
            print("✅ Schema matrix collected and saved.")

    if args.full_report:
        records = load_normalized_records(site_name)
        config = ConfigManager().as_dict()
        cli_flags = vars(args)
        aggregate_and_print(records, site_name, config, cli_flags)

    if args.score_drift:
        from analytics.score_drift_export import generate_drift_csv

        generate_drift_csv(site=args.site)

    if args.plugin_diff:
        from analytics.plugin_usage_diff import run_plugin_diff

        run_plugin_diff(site=args.site)


if __name__ == "__main__":
    main()
