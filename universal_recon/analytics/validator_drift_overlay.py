# === analytics/validator_drift_overlay.py ===

import json
from datetime import datetime
from pathlib import Path

TEMPLATE = """
<html><head>
<title>Validator Drift Overlay</title>
<link rel="stylesheet" href="assets/style_overlay.css">
</head><body>
<h2>🔻 Validator Drift Overview – {date}</h2>
<table>
<tr><th>Site</th><th>Score</th><th>Status</th><th>Tags</th></tr>
{rows}
</table>
</body></html>
"""


def render_row(site, data):
    score = data.get("score_summary", {}).get("field_score", "–")
    tags = ", ".join(data.get("domain_tags", [])) or "–"
    state = data.get("site_validation_state", "ok")
    icon = "🔻" if data.get("validator_drift") else "→"
    style = " style='background:#fdd'" if state in ("regressed", "critical") else ""
    return f"<tr{style}><td>{site}</td><td>{score}</td><td>{icon} {state}</td><td>{tags}</td></tr>"


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
