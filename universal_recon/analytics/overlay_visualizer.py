# === analytics/overlay_visualizer.py ===

import argparse
import json
from datetime import datetime
from pathlib import Path

TEMPLATE = """
<html>
<head><title>📊 Multi-site Schema Overlay</title>
<link rel="stylesheet" href="assets/style_overlay.css">
</head>
<body>
<h2>📊 Schema Matrix Overview – {date}</h2>
<table>
<tr><th>Site</th><th>Score</th><th>Drift</th><th>Plugins</th><th>Tags</th><th>Anomalies</th></tr>
{rows}
</table>
</body>
</html>
"""


def render_row(site, entry):
    score = entry.get("score_summary", {}).get("field_score", "–")
    drift = entry.get("validator_drift", False)
    drift_symbol = "↑" if drift == "up" else "↓" if drift == "down" else "→"
    plugins = ", ".join(entry.get("plugins_used", [])) or "–"
    tags = ", ".join(entry.get("domain_tags", [])) or "–"
    anomalies = ", ".join(entry.get("anomaly_flags", [])) or "–"
    return f"<tr><td>{site}</td><td>{score}</td><td>{drift_symbol}</td><td>{plugins}</td><td>{tags}</td><td>{anomalies}</td></tr>"


def generate_overlay(
    matrix_path="output/schema_matrix.json", output_path="output/dashboard_overlay.html"
):
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)
    rows = [render_row(site, data) for site, data in matrix.get("sites", {}).items()]
    html = TEMPLATE.format(
        rows="\n".join(rows), date=datetime.today().strftime("%Y-%m-%d")
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] HTML overlay dashboard saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-path", default="output/schema_matrix.json")
    parser.add_argument("--output-html", default="output/dashboard_overlay.html")
    args = parser.parse_args()
    generate_overlay(args.matrix_path, args.output_html)
