# universal_recon/utils/recon_summary_builder.py

import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)


def run_analysis(records, config=None):
    summary = summarize_records(records)
    return summary


def summarize_records(records: List[Dict]) -> Dict:
    """
    Summarizes ranked, normalized, and grouped records.
    Outputs stats like completeness, top-ranked fields, and plugin coverage.
    """
    summary = {
        "total_records": len(records),
        "field_type_counts": defaultdict(int),
        "plugin_counts": defaultdict(int),
        "strongest_fields": defaultdict(int),
        "score_distribution": [],
        "incomplete_records": 0,
    }

    for record in records:
        r_type = record.get("type", "unknown")
        source = record.get("source", "unknown")
        score = record.get("score", 0)

        summary["field_type_counts"][r_type] += 1
        summary["plugin_counts"][source] += 1
        summary["score_distribution"].append(score)

        if record.get("strongest") is True:
            summary["strongest_fields"][r_type] += 1

        # Check for incomplete records
        required_fields = ["type", "value", "xpath", "context", "url"]
        if not all(record.get(f) for f in required_fields):
            summary["incomplete_records"] += 1

    # Aggregate stats
    summary["score_distribution"].sort(reverse=True)
    summary["average_score"] = round(
        sum(summary["score_distribution"]) / max(1, len(summary["score_distribution"])), 2
    )
    summary["completeness_rate"] = round(
        (len(records) - summary["incomplete_records"]) / max(1, len(records)), 2
    )

    return summary


def print_summary(summary: Dict):
    """
    Prints a human-readable summary to CLI.
    """
    logger.info("🧠 Recon Summary Report")
    logger.info(f"Total Records: {summary['total_records']}")
    logger.info(f"Average Field Score: {summary['average_score']}")
    logger.info(f"Completeness Rate: {summary['completeness_rate'] * 100:.1f}%")
    logger.info(f"Incomplete Records: {summary['incomplete_records']}")
    logger.info("Field Counts:")
    for k, v in summary["field_type_counts"].items():
        logger.info(f"  - {k}: {v}")
    logger.info("Strongest Fields:")
    for k, v in summary["strongest_fields"].items():
        logger.info(f"  - {k}: {v}")
    logger.info("Plugin Contribution:")
    for k, v in summary["plugin_counts"].items():
        logger.info(f"  - {k}: {v}")
