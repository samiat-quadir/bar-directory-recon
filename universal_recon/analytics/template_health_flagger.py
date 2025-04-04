# universal_recon/analytics/template_health_flagger.py

from typing import List, Dict

def run_analysis(records: List[Dict] = None) -> Dict:
    if records is None:
        records = [{"template_id": 1, "health": "unknown"}]

    flagged = [r for r in records if r.get("health") == "unknown"]
    return {
        "plugin": "template_health_flagger",
        "flagged": len(flagged),
        "total": len(records)
    }

def run_analysis(records, config=None):
    return flag_template_health(records)
