# === analytics/schema_dashboard_stub.py ===

import json
from pathlib import Path

def print_schema_summary(matrix_path="output/schema_matrix.json"):
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)
    print("\n📊 Schema Dashboard")
    for site, data in matrix.get("sites", {}).items():
        score = data.get("score_summary", {}).get("field_score", "–")
        tags = ", ".join(data.get("domain_tags", []))
        print(f" - {site}: {score} points [{tags}]")
