# validators/firm_name_matcher.py

from typing import Dict, List

KNOWN_SUFFIXES = ["LLP", "LLC", "Inc.", "P.C.", "PLC", "Co."]


def normalize_firm_name(name: str) -> str:
    return name.replace(",", "").replace(".", "").lower()


def run_analysis(records=None, config=None):
    if records is None:
        records = [{"type": "firm_name", "value": "Example LLP", "rank": 1, "plugin": "test"}]
    return {"plugin": "firm_name_matcher", "results": validate_firm_names(records)}


def validate_firm_names(fields: List[Dict]) -> List[Dict]:
    results = []
    for field in fields:
        if field.get("type") != "firm_name":
            continue

        value = field.get("value", "")
        norm = normalize_firm_name(value)
        has_suffix = any(suffix.lower().replace(".", "") in norm for suffix in KNOWN_SUFFIXES)

        results.append(
            {
                "type": "firm_name",
                "value": value,
                "valid": has_suffix,
                "error": None if has_suffix else "Missing known suffix",
                "score": 5 if has_suffix else 3,
                "rank": field.get("rank", 0),
                "plugin": "firm_name_matcher",
                "severity": "none" if has_suffix else "warning",
            }
        )
    return results
