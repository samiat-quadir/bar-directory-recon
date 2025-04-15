# main.py

import sys
import argparse
import os

def main():
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

    args = parser.parse_args()

    # 1) Collect fieldmap
    if args.schema_collect:
        from analytics.site_schema_collector import collect_site_schema
        site_name = args.site or "default_site"
        fieldmap_path = collect_site_schema(site_name, verbose=args.verbose)
        if args.verbose:
            print(f"✅ Fieldmap collected at: {fieldmap_path}")

    # 2) Lint fieldmap
    if args.schema_lint:
        from validators.fieldmap_validator import validate_fieldmap
        site_name = args.site or "default_site"
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        result = validate_fieldmap(path, verbose=args.verbose)
        if args.verbose:
            print(f"✅ Lint result: {result}")

    # 3) Score fieldmap
    if args.schema_score:
        from analytics.schema_score_linter import score_fieldmap
        site_name = args.site or "default_site"
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        result = score_fieldmap(path, verbose=args.verbose)
        if args.verbose:
            print(f"✅ Score result: {result}")

    # 4) Domain-lint logic
    if args.domain_lint:
        from validators.fieldmap_domain_linter import domain_lint_fieldmap
        site_name = args.site or "default_site"
        path = f"output/fieldmap/{site_name}_fieldmap.json"
        result = domain_lint_fieldmap(path, verbose=args.verbose)
        if args.verbose:
            print(f"✅ Domain-lint result: {result}")

    # 5) Multi-site schema matrix
    if args.schema_matrix:
        from analytics.schema_matrix_collector import collect_schema_matrix, write_schema_matrix
        from datetime import datetime
        import shutil
    matrix_path = "output/schema_matrix.json"
    archive_dir = "output/archive"
    os.makedirs(archive_dir, exist_ok=True)

    # Archive existing matrix if it exists
    if os.path.exists(matrix_path):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archived_path = os.path.join(archive_dir, f"schema_matrix_{timestamp}.json")
        shutil.copy(matrix_path, archived_path)
        if args.verbose:
            print(f"📦 Archived previous matrix to: {archived_path}")

    # Collect new matrix and overwrite the original
    matrix = collect_schema_matrix(output_dir="output/fieldmap")
    write_schema_matrix(matrix, save_path=matrix_path, verbose=args.verbose)


    # 6) Full report aggregator
    if args.full_report:
        from plugin_aggregator import aggregator_logic
        site_name = args.site or "default_site"
        aggregator_logic(site_name, verbose=args.verbose)

    if args.export_html:
        from analytics.overlay_visualizer import main as overlay_main
        overlay_main()

    # 7) Schema trend dashboard
    if args.dashboard:
        from analytics.schema_trend_dashboard import main as dash_main
        dash_main()

    # 8) Validator drift tracker
    if args.drift_check:
        from analytics.validator_drift_tracker import main as drift_main
        drift_main()

    # 9) Plugin score overlay
    if args.plugin_overlay:
        from analytics.plugin_score_overlay import main as plugin_overlay_main
        plugin_overlay_main()

    # 10) Export CSV summary
    if args.export_csv:
        from analytics.export_csv_summary import main as csv_export_main
        csv_export_main()

    # 12) Plugin heatmap
    if args.heatmap_plugin:
        from analytics.heatmap_plugin_usage import main as plugin_heatmap_main
        plugin_heatmap_main()

    # 13) Score drift heatmap
    if args.heatmap_drift:
        from analytics.heatmap_score_drift import main as drift_heatmap_main
        drift_heatmap_main()

    if args.verbose:
        print("✅ CLI run completed successfully.")

if __name__ == "__main__":
    main()
