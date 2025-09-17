# universal_recon/utils/phase_27_health_report.py

import json
import os
import time

OUTPUT_DIR = "output"
STATUS_JSON = os.path.join(OUTPUT_DIR, "output_status.json")
SCHEMA_MATRIX = os.path.join(OUTPUT_DIR, "schema_matrix.json")
VALIDATION_MATRIX = "universal_recon/validators/validation_matrix.yaml"
HEALTH_HTML = os.path.join(OUTPUT_DIR, "phase_27_health_report.html")

STALE_THRESHOLD_HOURS = 24


def check_file(path):
    return os.path.exists(path)


def check_staleness(path):
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    age_hours = (time.time() - mtime) / 3600
    return age_hours


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def emit_html(status, stale_warnings, missing):
    rows = []
    for site, info in status.items():
        drift = info.get("validator_drift", False)
        health = info.get("site_health", "unknown").upper()
        plugins = ", ".join(info.get("plugins_removed", [])) or "None"
        penalty = info.get("score_suppressed_by", 0)
        color = {"OK": "#2ecc71", "WARNING": "#f1c40f", "DEGRADED": "#e74c3c"}.get(
            health, "#ccc"
        )
        drift_badge = "✅" if not drift else "⚠️"
        rows.append(
            f"<tr><td>{site}</td><td style='color:{color}'>{health}</td>"
            f"<td>{drift_badge}</td><td>{plugins}</td><td>{penalty}%</td></tr>"
        )

    html = [
        "<html><head><title>Phase 27 Health Report</title></head><body>",
        "<h2>📊 Universal Recon – Phase 27 Health Summary</h2>",
        "<table border='1' cellpadding='5'><tr><th>Site</th><th>Health</th><th>Validator Drift</th><th>Plugins Removed</th><th>Penalty</th></tr>",
    ]
    html += rows
    html.append("</table><br><h3>🟠 Warnings</h3><ul>")
    for w in stale_warnings:
        html.append(f"<li>{w}</li>")
    for m in missing:
        html.append(f"<li>❌ Missing: {m}</li>")
    html.append("</ul></body></html>")

    os.makedirs(os.path.dirname(HEALTH_HTML), exist_ok=True)
    with open(HEALTH_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[✓] Phase 27 health report written to: {HEALTH_HTML}")


def main():
    status = load_json(STATUS_JSON)
    stale_warnings = []
    missing = []

    for path in [SCHEMA_MATRIX, VALIDATION_MATRIX, STATUS_JSON]:
        if not check_file(path):
            missing.append(path)
        else:
            age = check_staleness(path)
            if age and age > STALE_THRESHOLD_HOURS:
                stale_warnings.append(f"{path} is stale ({age:.1f}h old)")

    emit_html(status, stale_warnings, missing)


if __name__ == "__main__":
    main()
