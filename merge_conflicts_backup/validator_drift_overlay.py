# === analytics/validator_drift_overlay.py ===

import json
from datetime import datetime
from pathlib import Path

<<<<<<< HEAD
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
=======
BADGE_COLORS = {
    "critical": "#e74c3c",  # red
    "warning": "#f39c12",  # orange
    "info": "#3498db",  # blue
}


def load_status(path="output/output_status.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def export_html(status, path="output/validator_drift_overlay.html"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    html = ["<html><head><title>Validator Drift Overlay</title></head><body>"]
    html.append("<h1>🔍 Validator Plugin Drift Summary</h1>")
>>>>>>> 3ccf4fd (Committing all changes)


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

<<<<<<< HEAD
=======
    html.append("</body></html>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[✓] Validator drift overlay written to: {path}")


def export_json(status, path="output/validator_drift_overlay.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    print(f"[✓] Validator drift overlay JSON written to: {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--status-json", default="output/output_status.json")
    parser.add_argument("--output-html", default="output/validator_drift_overlay.html")
    parser.add_argument("--output-json", default="output/validator_drift_overlay.json")
    args = parser.parse_args()

    status = load_status(args.status_json)
    if not status:
        print("❌ No status summary found.")
        return
    export_html(status, args.output_html)
    export_json(status, args.output_json)
>>>>>>> 3ccf4fd (Committing all changes)


if __name__ == "__main__":
    run_overlay()
