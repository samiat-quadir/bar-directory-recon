# analytics/validator_drift_overlay.py

import json
import argparse
from pathlib import Path
from datetime import datetime

HTML_TEMPLATE = """
<html>
<head><title>Validator Drift Overlay</title>
<style>
  body { font-family: sans-serif; margin: 2em; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
  th { background-color: #f4f4f4; }
  .regressed { background-color: #fdd; color: #900; font-weight: bold; }
</style>
</head>
<body>
<h2>🔻 Validator Drift Overlay – {date}</h2>
<table>
<tr><th>Site</th><th>Status</th><th>Score</th><th>Drift</th><th>Tags</th></tr>
{rows}
</table>
</body>
</html>
"""

def load_matrix(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def render_rows(data):
    rows = []
    sites = data.get("sites", {})
    for site, info in sites.items():
        state = info.get("site_validation_state", "ok")
        drift = "🔻" if info.get("validator_drift") else "" 
        score = info.get("score_summary", {}).get("field_score", "-")
        tags = ", ".join(info.get("domain_tags", []))
        cls = "regressed" if state != "ok" else ""
        rows.append(f"<tr class='{cls}'><td>{site}</td><td>{state}</td><td>{score}</td><td>{drift}</td><td>{tags}</td></tr>")
    return "\n".join(rows)

def generate_overlay(input_path, output_path):
    data = load_matrix(input_path)
    rows_html = render_rows(data)
    html = HTML_TEMPLATE.format(rows=rows_html, date=datetime.today().strftime("%Y-%m-%d"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] Drift overlay written to: {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", default="output/schema_matrix.json")
    parser.add_argument("--output", default="output/validator_drift_overlay.html")
    args = parser.parse_args()
    generate_overlay(args.matrix, args.output)

if __name__ == "__main__":
    main()
