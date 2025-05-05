# === analytics/validator_drift_overlay.py ===

import json
from datetime import datetime
from pathlib import Path


def run_overlay(
    matrix_path="output/schema_matrix.json",
    output_html="output/validator_drift_overlay.html",
):
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)
    rows = [render_row(site, data) for site, data in matrix.get("sites", {}).items()]
    html = TEMPLATE.format(rows="\n".join(rows), date=datetime.today().strftime("%Y-%m-%d"))
    Path(output_html).parent.mkdir(parents=True, exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] Drift overlay written to: {output_html}")


if __name__ == "__main__":
    run_overlay()
