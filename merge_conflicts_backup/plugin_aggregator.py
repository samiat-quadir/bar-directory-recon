# === universal_recon/plugin_aggregator.py ===

import json
import os
from datetime import datetime
from pathlib import Path

<<<<<<< HEAD
from analytics.risk_analysis import run_analysis as run_risk_analysis
from analytics.schema_score_linter import run_schema_score_lint
from analytics.score_heatmap_overlay import run_analysis as run_heatmap_overlay
from analytics.trend_badge_tracker import run_analysis as run_trend_tracker
from plugin_loader import load_plugins_by_type
from report_printer import print_audit, print_health, print_schema_score, print_summary, print_trend
=======
from universal_recon.core.report_printer import print_audit, print_health, print_summary, print_trend
>>>>>>> 3ccf4fd (Committing all changes)


def archive_previous_matrix():
    src = Path("output/schema_matrix.json")
    if src.exists():
        archive_dir = Path("output/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        dst = archive_dir / f"schema_matrix_{timestamp}.json"
        src.rename(dst)
        print(f"[archiver] Moved previous matrix to: {dst}")


def aggregate_and_print(records, site_name, config, cli_flags):
    output_dir = os.path.join("output", "reports")
    os.makedirs(output_dir, exist_ok=True)

    summary = {"total_records": len(records)}
    audit_results = {
        "plugin": "audit_score_matrix_generator",
        "total_records": len(records),
    }
    trend = {"plugin": "trend_dashboard_stub", "site": site_name}
    health = {"plugin": "template_health_flagger", "site": site_name}

    if cli_flags.get("verbose"):
        print_summary(summary)
        print_audit(audit_results)
        print_trend(trend)
        print_health(health)

    heatmap_result = run_heatmap_overlay(records, config={"site_name": site_name})
    if cli_flags.get("verbose"):
        print("[heatmap] Score Heatmap Overlay completed.")

    trend_result = run_trend_tracker(config={"site_name": site_name, "output_dir": output_dir})
    if trend_result and cli_flags.get("verbose"):
        print("[trend] Trend Badge Tracker completed.")

    schema_score_result = None
    if cli_flags.get("schema_score"):
        fieldmap_path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
        schema_score_result = run_schema_score_lint(fieldmap_path)
        if schema_score_result and cli_flags.get("verbose"):
            print_schema_score(schema_score_result)

    risk_result = run_risk_analysis(config={"site_name": site_name})
    if risk_result and cli_flags.get("verbose"):
        print("[risk] Plugin Risk Ranking Complete")

    full_report = {
        "site": site_name,
        "summary": summary,
        "audit": audit_results,
        "trend": trend_result,
        "heatmap": heatmap_result,
        "schema_score": schema_score_result,
<<<<<<< HEAD
        "risk_profile": risk_result,
=======
        "risk_profile": {},
        "plugins_used": sorted(list(plugins_used)),
>>>>>>> 3ccf4fd (Committing all changes)
    }

    full_path = os.path.join(output_dir, f"{site_name}_full_report.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    if cli_flags.get("schema_matrix"):
        archive_previous_matrix()
        matrix = {
            "site": site_name,
            "plugins": load_plugins_by_type(records),
            "summary": summary,
            "audit": audit_results,
            "trend": trend_result,
            "heatmap": heatmap_result,
            "schema_score": schema_score_result,
            "risk_profile": risk_result,
        }
