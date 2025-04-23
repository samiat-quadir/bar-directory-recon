# === analytics/validator_drift_overlay.py ===

import json
import argparse
from pathlib import Path

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Validator Drift Overlay</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
    .critical {{ background-color: #f8d7da; color: #721c24; }}
    .warning {{ background-color: #fff3cd; color: #856404; }}
    .info {{ background-color: #d1ecf1; color: #0c5460; }}
  </style>
</head>
<body>
  <h1>🚨 Validator Drift Overlay</h1>
  <p>Snapshot: {snapshot}</p>
  <table>
    <thead>
      <tr><th>Site</th><th>Validator</th><th>Severity</th><th>Reason</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""

def load_schema_matrix(matrix_path):
    with open(matrix_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_overlay_html(matrix, snapshot):
    rows = []
    for site, data in matrix.get("sites", {}).items():
        for flag in data.get("validator_risk_flags", []):
            severity = flag.get("severity", "info").lower()
            validator = flag.get("validator")
            reason = flag.get("reason", "No reason provided.")
            row = f"<tr class='{severity}'><td>{site}</td><td>{validator}</td><td>{severity.upper()}</td><td>{reason}</td></tr>"
            rows.append(row)
    return HTML_TEMPLATE.format(snapshot=snapshot, rows="\n".join(rows))

def main():
    parser = argparse.ArgumentParser(description="Validator Drift Overlay Generator")
    parser.add_argument("--matrix-path", default="output/schema_matrix.json", help="Path to schema_matrix.json")
    parser.add_argument("--output-html", default="output/validator_drift_overlay.html", help="Where to write the HTML file")
    args = parser.parse_args()

    matrix_path = Path(args.matrix_path)
    if not matrix_path.exists():
        print(f"❌ Matrix not found: {matrix_path}")
        return

    matrix = load_schema_matrix(matrix_path)
    snapshot_name = matrix_path.stem
    html = generate_overlay_html(matrix, snapshot=snapshot_name)

    output_path = Path(args.output_html)
    output_path.write_text(html, encoding="utf-8")
    print(f"[✓] Validator drift overlay written to: {output_path.resolve()}")

if __name__ == "__main__":
    main()
