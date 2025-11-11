import json
import os
from collections import defaultdict
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


def save_trend_report(site_name: str, trend_summary: Dict):
    os.makedirs("output/reports", exist_ok=True)
    path = f"output/reports/{site_name}_trend.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trend_summary, f, indent=2)
    return path
