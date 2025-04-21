import os
import json
from pathlib import Path
from datetime import datetime

from plugin_loader import load_plugins_by_type, load_normalized_records
from report_printer import print_summary, print_audit, print_trend, print_health, print_schema_score

from analytics.score_heatmap_overlay import run_analysis as run_heatmap_overlay
from analytics.trend_badge_tracker import run_analysis as run_trend_tracker
from analytics.plugin_health_visualizer import run_analysis as run_risk_analysis
from analytics.schema_score_linter import run_schema_score_lint


def archive_previous_matrix():
    """
    Move the existing schema_matrix.json to the archive with a timestamp.
    """
    src = Path("output/schema_matrix.json")
    if src.exists():
        archive_dir = Path("output/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        dst = archive_dir / f"schema_matrix_{timestamp}.json"
        src.rename(dst)
        print(f"[archiver] Moved previous matrix to: {dst}")


def aggregate_and_print(records, site_name, config, cli_flags):
    """
    Aggregates plugin outputs, calls overlays, and prints report summaries.
    """
    output_dir = os.path.join("output", "reports")
    os.makedirs(output_dir, exist_ok=True)

    summary = {
        "site": site_name,
        "total_records": len(records),
        "valid_count": 0,
        "invalid_count": 0
    }

    # Placeholder: calculate counts from records if needed
    audit_results = {"plugin": "audit_score_matrix_generator", "total_records": len(records)}
    trend = {"plugin": "trend_dashboard_stub", "site": site_name}
    health = {"plugin": "template_health_flagger", "site": site_name}

    if cli_flags.get("verbose"):
        print("\n📝 Recon Summary Report")
        print_summary(summary)
        print("\n🧾 Audit Summary")
        print_audit(audit_results)
        print("\n📈 Trend Analysis")
        print_trend(trend)
        print("\n🏥 Health Flags")
        print_health(health)

    # Run plugin overlays
    heatmap_result = run_heatmap_overlay(records, config={"site_name": site_name})
    if cli_flags.get("verbose"):
        print("[heatmap] Score Heatmap Overlay completed.")

    trend_result = run_trend_tracker(config={"site_name": site_name, "output_dir": output_dir})
    if cli_flags.get("verbose"):
        print("[trend] Trend Badge Tracker completed.")

    schema_score_result = None
    if cli_flags.get("schema_score"):
        fieldmap_path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
        schema_score_result = run_schema_score_lint(fieldmap_path)
        if schema_score_result and cli_flags.get("verbose"):
            print_schema_score(schema_score_result)

    risk_result = run_risk_analysis(config={"site_name": site_name})
    if cli_flags.get("verbose") and risk_result:
        print("[risk] Plugin Risk Ranking completed.")

    full_report = {
        "site": site_name,
        "summary": summary,
        "audit": audit_results,
        "trend": trend_result,
        "heatmap": heatmap_result,
        "schema_score": schema_score_result,
        "risk_profile": risk_result,
    }

    full_path = os.path.join(output_dir, f"{site_name}_full_report.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    if cli_flags.get("schema_matrix"):
        archive_previous_matrix()
