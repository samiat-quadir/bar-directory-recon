"""
Audit Report Generator module for analyzing record data quality.
This module provides functionality to generate audit reports that summarize
record quality, score distributions, and validation errors by plugin.
"""
from collections import defaultdict


def generate_audit_report(records):
    """
    Generate an audit report summarizing record quality metrics.

    Args:
        records (list): List of record dictionaries with type, value, plugin, and score keys

    Returns:
        dict: Audit report with total records, score tiers, and validator errors by plugin
    """
    # Initialize the report structure
    report = {
        "total_records": len(records),
        "score_tiers": {"critical": 0, "warning": 0, "clean": 0},
        "validator_errors_by_plugin": defaultdict(list),
    }

    # Process each record
    for record in records:
        score = record.get("score", 0)
        plugin = record.get("plugin", "unknown")
        value = record.get("value", "")
        record_type = record.get("type", "unknown")

        # Categorize by score tier
        if score <= 1:
            report["score_tiers"]["critical"] += 1

            # Add to validator errors if empty or low score
            if value == "" or score == 0:
                report["validator_errors_by_plugin"][plugin].append(
                    {"type": record_type, "value": value, "score": score, "issue": "Missing or invalid value"}
                )

        elif score <= 3:
            report["score_tiers"]["warning"] += 1

            # Add to validator errors if warning level
            report["validator_errors_by_plugin"][plugin].append(
                {"type": record_type, "value": value, "score": score, "issue": "Potential data quality issue"}
            )

        else:
            report["score_tiers"]["clean"] += 1

    # Convert defaultdict to regular dict for serialization
    report["validator_errors_by_plugin"] = dict(report["validator_errors_by_plugin"])

    return report
