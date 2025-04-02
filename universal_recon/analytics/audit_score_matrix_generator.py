# audit_score_matrix_generator.py

from collections import defaultdict
from typing import List, Dict

def run_analysis(records: List[Dict], config: Dict = None) -> Dict:
    """
    Aggregates validator severity counts per plugin and field.
    Returns a nested dict for audit scoring matrix.
    """
    matrix = defaultdict(lambda: defaultdict(lambda: {"critical": 0, "warning": 0, "info": 0}))

    for record in records:
        plugin = record.get("plugin", "unknown")
        field_type = record.get("type", "unknown")
        severity = record.get("severity", "info")

        if severity in matrix[plugin][field_type]:
            matrix[plugin][field_type][severity] += 1

    return {
        "audit_score_matrix": matrix
    }
