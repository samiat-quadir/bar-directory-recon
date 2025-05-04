# universal_recon/utils/template_clusterer.py

from collections import defaultdict
from typing import Dict, List


def generate_template(records: List[Dict]) -> List[Dict]:
    """
    Group normalized records into profile templates based on shared identity traits.
    """
    clusters = []

    # Index by identity traits (e.g., name, email, firm)
    identity_keys = ["email", "name", "firm_name"]

    def extract_key(record):
    """TODO: Add docstring."""
        for key in identity_keys:
            if record.get("type") == key and record.get("value"):
                return (key, record["value"].lower())
        return None

    grouped = defaultdict(list)
    for record in records:
        key = extract_key(record)
        if key:
            grouped[key].append(record)
        else:
            # Records without identity anchors go into their own buckets
            fallback_key = (record.get("type", "unknown"), record.get("xpath", ""))
            grouped[fallback_key].append(record)

    for group in grouped.values():
        profile = {
            "fields": group,
            "completeness": "unknown",  # updated later by completeness checker
            "rank_summary": {},  # optionally filled by ranker
            "source_plugins": list(set(r.get("source") for r in group if r.get("source"))),
        }
        clusters.append(profile)

    return clusters
