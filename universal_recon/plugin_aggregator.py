# universal_recon/plugin_aggregator.py

import json
import os
from datetime import datetime
from pathlib import Path

from universal_recon.core.report_printer import (
    print_audit,
    print_health,
    print_summary,
    print_trend,
)


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

    schema_score_result = None
    plugins_used = set()
    for record in records:
        plugin_name = record.get("plugin")
        if plugin_name:
            plugins_used.add(plugin_name)

    full_report = {
        "site": site_name,
        "summary": summary,
        "audit": audit_results,
        "trend": trend,
        "schema_score": schema_score_result,
        "risk_profile": {},
        "plugins_used": sorted(list(plugins_used)),
    }

    full_path = os.path.join(output_dir, f"{site_name}_full_report.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    if cli_flags.get("schema_matrix"):
        archive_previous_matrix()
