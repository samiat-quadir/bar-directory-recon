# universal_recon/utils/status_html_emitter.py

import json
from pathlib import Path

HTML_PATH = Path("output/status_summary.html")
STATUS_JSON = Path("output/output_status.json")


def site_health_color(health):
    return {"ok": "🟩", "warning": "🟧", "degraded": "🟥"}.get(health, "❔")


def emit_status_html():
    if not STATUS_JSON.exists():
        print("❌ output_status.json not found.")
        return

    with open(STATUS_JSON, "r", encoding="utf-8") as f:
        status_data = json.load(f)

    rows = []
    for site, data in status_data.items():
        icon = site_health_color(data.get("site_health", "unknown"))
        plugins = ", ".join(data.get("plugins_removed", [])) or "None"
        drift = "Yes" if data.get("validator_drift") else "No"
        health = data.get("site_health", "unknown").capitalize()

        row = f"""
        <tr>
          <td><b>{site}</b></td>
          <td>{icon} {health}</td>
          <td>{drift}</td>
          <td>{plugins}</td>
        </tr>
        """
        rows.append(row)

    html = f"""
    <html>
    <head>
      <title>Validator Drift Status</title>
      <style>
        body {{ font-family: sans-serif; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 8px; border: 1px solid #ccc; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
      </style>
    </head>
    <body>
      <h2>Validator Drift Summary</h2>
      <table>
        <tr>
          <th>Site</th>
          <th>Health</th>
          <th>Validator Drift</th>
          <th>Plugins Removed</th>
        </tr>
        {''.join(rows)}
      </table>
    </body>
    </html>
    """

    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"✅ Status HTML written to: {HTML_PATH}")


if __name__ == "__main__":
    emit_status_html()
