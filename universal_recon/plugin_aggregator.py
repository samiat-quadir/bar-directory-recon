# === universal_recon/plugin_aggregator.py ===

import os
import json
from pathlib import Path
from datetime import datetime

from plugin_loader import load_plugins_by_type
from core.report_printer import print_summary, print_audit, print_trend, print_health, print_schema_score
from analytics.schema_score_linter import run_schema_score_lint
from analytics.trend_badge_tracker import run_analysis as run_trend_tracker

def archive_previous_matrix():
    src = Path("output/schema_matrix.json")
    if src.exists():
        archive_dir = Path("output/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        dst = archive_dir / f"schema_matrix_{timestamp}.json"
        src.rename(dst)
        print(f"[archiver] Moved previous matrix to: {dst}")

def extract_plugins_used(records):
    used = set()
    for record in records:
        plugins = record.get("plugin", None)
        if isinstance(plugins, str):
            used.add(plugins)
        elif isinstance(plugins, list):
            used.update(plugins)
    return sorted(used)

def aggregate_and_print(records, site_name, config, cli_flags):
    output_dir = os.path.join("output", "reports")
    os.makedirs(output_dir, exist_ok=True)

    summary = {"total_records": len(records)}
    audit_results = {"plugin": "audit_score_matrix_generator", "total_records": len(records)}
    trend_result = run_trend_tracker(config={"site_name": site_name, "output_dir": output_dir})
    health = {"plugin": "template_health_flagger", "site": site_name}

    if cli_flags.get("verbose"):
        print_summary(summary)
        print_audit(audit_results)
        print_trend(trend_result)
        print_health(health)

    schema_score_result = None
    if cli_flags.get("schema_score"):
        fieldmap_path = os.path.join("output", "fieldmap", f"{site_name}_fieldmap.json")
        schema_score_result = run_schema_score_lint(fieldmap_path)
        if schema_score_result and cli_flags.get("verbose"):
            print_schema_score(schema_score_result)

    full_report = {
        "site": site_name,
        "summary": summary,
        "audit": audit_results,
        "trend": trend_result,
        "heatmap": None,
        "schema_score": schema_score_result,
        "risk_profile": None,
    }

    full_path = os.path.join(output_dir, f"{site_name}_full_report.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    if cli_flags.get("schema_matrix"):
        archive_previous_matrix()
        matrix_output_path = "output/schema_matrix.json"

        matrix = {
            "sites": {
                site_name: {
                    "summary": summary,
                    "plugins_used": extract_plugins_used(records),
                    "score_summary": schema_score_result or {},
                    "trend_data": trend_result or {},
                    "domain_tags": config.get("domain_tags", []),
                    "anomaly_flags": config.get("anomaly_flags", [])
                }
            }
        }

        with open(matrix_output_path, "w", encoding="utf-8") as f:
            json.dump(matrix, f, indent=2)

        print(f"[✓] Schema matrix written to: {matrix_output_path}")
