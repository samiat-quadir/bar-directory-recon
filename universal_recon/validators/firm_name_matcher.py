# universal_recon/validators/firm_name_matcher.py

from typing import Dict

def validate(record: Dict) -> Dict:
    firm_name = record.get("firm_name", "").lower()
    result = {
        "type": "firm_name",
        "value": firm_name,
        "valid": bool(firm_name and len(firm_name) > 2),
        "error": None if firm_name else "Missing or too short",
        "score": 2 if firm_name else 0,
        "rank": 1,
        "plugin": "firm_name_matcher",
        "severity": "critical" if not firm_name else "none",
    }
    return result
