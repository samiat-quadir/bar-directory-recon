"""Generate audit reports for validator health."""

from typing import Dict, List

from universal_recon.core.logger import get_logger

logger = get_logger(__name__)


def generate_audit_report(records: List[Dict]) -> Dict:
    """Generate audit report from validation records."""
    try:
        report = {
            "total_records": len(records),
            "score_tiers": {"critical": 0, "warning": 0, "clean": 0},
            "validator_errors_by_plugin": {},
        }

        for record in records:
            score = record.get("score", 0)
            plugin = record.get("plugin", "unknown")

            if score < 2:
                report["score_tiers"]["critical"] += 1
            elif score < 4:
                report["score_tiers"]["warning"] += 1
            else:
                report["score_tiers"]["clean"] += 1

            if score < 4:  # Track errors for non-clean records
                if plugin not in report["validator_errors_by_plugin"]:
                    report["validator_errors_by_plugin"][plugin] = 0
                report["validator_errors_by_plugin"][plugin] += 1

        return report
    except Exception as e:
        logger.error(f"Error generating audit report: {e}")
        return {"total_records": 0, "score_tiers": {}, "validator_errors_by_plugin": {}}
