import json
import os
<<<<<<< HEAD
=======
from collections import defaultdict
>>>>>>> bf5b0be (🧽 Fix all Flake8 + formatting issues across universal_recon/)
from typing import Dict, List


def load_summaries_from_directory(directory: str) -> List[Dict]:
    summaries = []
    for filename in os.listdir(directory):
        if filename.endswith("_summary.json"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
                summaries.append(json.load(f))
    return summaries


def run_analysis(records, config=None):
    return analyze_trends(records)


<<<<<<< HEAD
def analyze_trends(site_name: str, summaries: List[Dict]) -> Dict:
    """
    Analyze trends across multiple summary reports.

    Args:
        site_name: Name of the site being analyzed
        summaries: List of summary dictionaries from different runs

    Returns:
        Dict containing trend analysis data
    """
    # Calculate differences between past and current data
    if len(summaries) < 2:
        return {"field_score_drift": {}, "plugin_activity_drift": {}, "field_absence_trends": {}}

    # For simplicity, we'll compare the most recent two summaries
    past_summary = summaries[0]
    current_summary = summaries[1]

    # Track field score drift
    field_score_drift = {}
    past_fields = past_summary.get("top_fields", {})
    current_fields = current_summary.get("top_fields", {})

    for field, past_count in past_fields.items():
        current_count = current_fields.get(field, 0)
        if current_count < past_count:
            field_score_drift[field] = past_count - current_count

    # Track plugin activity drift
    plugin_activity_drift = {}
    past_plugins = past_summary.get("plugin_usage", {})
    current_plugins = current_summary.get("plugin_usage", {})

    for plugin, past_count in past_plugins.items():
        current_count = current_plugins.get(plugin, 0)
        if current_count < past_count:
            plugin_activity_drift[plugin] = past_count - current_count

    # Track field absence trends
    field_absence_trends = {}
    for field, past_count in past_fields.items():
        current_count = current_fields.get(field, 0)
        if past_count > 0 and current_count == 0:
            field_absence_trends[field] = "disappeared"
        elif past_count > current_count:
            field_absence_trends[field] = "declining"

    return {
        "field_score_drift": field_score_drift,
        "plugin_activity_drift": plugin_activity_drift,
        "field_absence_trends": field_absence_trends,
    }

=======
def analyze_trends(summaries: List[Dict]) -> Dict:
    trend_data = {
        "total_runs": len(summaries),
        "field_presence": defaultdict(int),
        "plugin_usage": defaultdict(int),
        "score_volatility": defaultdict(list),
        "missing_field_flags": defaultdict(int),
    }

    for summary in summaries:
        for field in summary.get("top_fields", []):
            trend_data["field_presence"][field] += 1

        for plugin in summary.get("plugin_stats", {}):
            trend_data["plugin_usage"][plugin] += 1

        for record in summary.get("records", []):
            field_type = record.get("type")
            score = record.get("score") or record.get("predicted_score")
            if field_type and score is not None:
                trend_data["score_volatility"][field_type].append(score)
                if score < 3:
                    trend_data["missing_field_flags"][field_type] += 1

    # Calculate average scores and volatility
    trend_summary = {
        "total_runs": trend_data["total_runs"],
        "field_trend": {},
        "plugin_trend": dict(trend_data["plugin_usage"]),
    }

    for field, scores in trend_data["score_volatility"].items():
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        volatility = round(max(scores) - min(scores), 2) if len(scores) > 1 else 0
        trend_summary["field_trend"][field] = {
            "appearances": trend_data["field_presence"].get(field, 0),
            "avg_score": avg_score,
            "volatility": volatility,
            "low_score_flags": trend_data["missing_field_flags"].get(field, 0),
        }

    return trend_summary
>>>>>>> bf5b0be (🧽 Fix all Flake8 + formatting issues across universal_recon/)


def save_trend_report(site_name: str, trend_summary: Dict):
    os.makedirs("output/reports", exist_ok=True)
    path = f"output/reports/{site_name}_trend.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trend_summary, f, indent=2)
    return path
