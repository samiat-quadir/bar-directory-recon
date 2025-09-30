# === universal_recon/analytics/validator_drift_overlay.py ===

import json
import os

BADGE_COLORS = {
    "critical": "#e74c3c",  # red
    "warning": "#f39c12",  # orange
    "info": "#3498db",  # blue
}


def load_status(path="output/output_status.json"):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def export_html(status, path="output/validator_drift_overlay.html"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    html = ["<html><head><title>Validator Drift Overlay</title></head><body>"]
    html.append("<h1>🔍 Validator Plugin Drift Summary</h1>")

    for site, details in status.items():
        drift = details.get("validator_drift", False)
        health = details.get("site_health", "ok")
        plugins = details.get("plugins_removed", [])
        suppress = details.get("score_suppressed_by", 0)

        color = (
            "#2ecc71"
            if not drift
            else BADGE_COLORS.get("critical" if suppress >= 10 else "warning")
        )
        html.append("<div style='border:1px solid #ccc;margin:10px;padding:10px;'>")
        html.append(f"<h2>{site} - <span style='color:{color}'>{health.upper()}</span></h2>")
        if not drift:
            html.append("<p>✅ All validator plugins present.</p>")
        else:
            html.append("<ul>")
            for plugin in plugins:
                tooltip = f"Suppressed {suppress}% due to missing plugin: {plugin}"
                html.append(
                    f"<li><span title='{tooltip}' style='color:{color}'>{plugin}</span></li>"
                )
            html.append("</ul>")
            html.append(f"<p><b>Score Suppression:</b> {suppress}%</p>")
        html.append("</div>")

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


if __name__ == "__main__":
    main()
