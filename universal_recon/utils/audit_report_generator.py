import collections
from typing import List, Dict


def generate_audit_report(records: List[Dict]) -> Dict:
    """
    Generate an audit report with error breakdown, plugin usage, score tiers, and type counts.
    Compatible with recon_summary_builder.py format.
    """
    report = {
        "total_records": len(records),
        "errors": [],
        "score_tiers": {"critical": 0, "warning": 0, "clean": 0},
        "plugin_usage": collections.Counter(),
        "field_type_counts": collections.Counter(),
    }

    for record in records:
        record_type = record.get("type", "unknown")
        plugin = record.get("source", "unknown_plugin")
        score = record.get("score") or record.get("predicted_score", 0)
        error = record.get("error", None)

        # Count plugin + field type usage
        report["plugin_usage"][plugin] += 1
        report["field_type_counts"][record_type] += 1

        # Score tier
        if score >= 5:
            report["score_tiers"]["clean"] += 1
        elif 3 <= score < 5:
            report["score_tiers"]["warning"] += 1
        else:
            report["score_tiers"]["critical"] += 1

        # Capture validation error detail
        if error:
            report["errors"].append({
                "plugin": plugin,
                "type": record_type,
                "reason": error,
                "score_tier": (
                    "clean" if score >= 5 else
                    "warning" if score >= 3 else
                    "critical"
                )
            })

    # Convert counters to dicts for JSON serializability
    report["plugin_usage"] = dict(report["plugin_usage"])
    report["field_type_counts"] = dict(report["field_type_counts"])

    return report


def print_audit_summary(audit: Dict):
    """
    Print high-level audit summary for terminal or logs.
    """
    print("\n🔍 Audit Summary")
    print(f"  Total Records: {audit['total_records']}")
    print(f"  Errors: {len(audit['errors'])}")
    print("  Score Tiers:")
    for tier in ["critical", "warning", "clean"]:
        print(f"    - {tier.title()}: {audit['score_tiers'].get(tier, 0)}")
    print("  Plugin Usage:")
    for plugin, count in audit["plugin_usage"].items():
        print(f"    - {plugin}: {count}")
    print("  Field Types:")
    for field_type, count in audit["field_type_counts"].items():
        print(f"    - {field_type}: {count}")


def audit(records: List[Dict], print_summary: bool = True) -> Dict:
    audit_data = generate_audit_report(records)
    if print_summary:
        print_audit_summary(audit_data)
    return audit_data
