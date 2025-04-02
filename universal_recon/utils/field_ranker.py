# universal_recon/utils/field_ranker.py

from typing import List, Dict

FIELD_SCORES = {
    "name": 5,
    "email": 4,
    "firm_name": 3,
    "phone": 2,
    "bar_number": 2,
    "social_link": 1
}

def rank_records(records: List[Dict]) -> List[Dict]:
    """
    Assign score, rank, and strongest flag to normalized records.
    """
    # Assign score
    for record in records:
        record_type = record.get("type", "").lower()
        record["score"] = FIELD_SCORES.get(record_type, 0)

    # Group by type to rank within each field type
    by_type = {}
    for record in records:
        t = record.get("type")
        if t:
            by_type.setdefault(t, []).append(record)

    for record_type, group in by_type.items():
        # Sort by score descending
        sorted_group = sorted(group, key=lambda r: r.get("score", 0), reverse=True)
        for i, r in enumerate(sorted_group):
            r["rank"] = i + 1
            r["strongest"] = (i == 0)

    return records
