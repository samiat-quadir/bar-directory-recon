# trend_dashboard_stub.py
from typing import Dict


def run_analysis(trend_data: Dict, config: Dict = None) -> Dict:
    """
    Reads trend.json and outputs dashboard-style summaries: field drifts, plugin score changes.
    """
    dashboard = {
        "declining_fields": [],
        "plugin_drops": [],
        "notable_shifts": []
    }

    trends = trend_data.get("trends", {})

    for field, data in trends.items():
        if data.get("change") < -0.1:
            dashboard["declining_fields"].append({"field": field, **data})

    for plugin, stats in trend_data.get("plugin_usage", {}).items():
        if stats.get("change", 0) < -0.1:
            dashboard["plugin_drops"].append({"plugin": plugin, **stats})

    return {"trend_dashboard": dashboard}
