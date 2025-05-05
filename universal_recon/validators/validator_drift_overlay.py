# universal_recon/analytics/validator_drift_overlay.py

import json
import os

import yaml

from utils.validator_drift_badges import VALIDATOR_DRIFT_BADGES

BADGE_COLORS = {
    "critical": "#e74c3c",
    "warning": "#f39c12",
    "info": "#3498db",
    "ok": "#2ecc71",
}


def load_matrix(matrix_path):
    with open(matrix_path) as f:
        return json.load(f)


def load_validation_yaml(yaml_path="validation_matrix.yaml"):
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def load_status_json(status_path="output/output_status.json"):
    if os.path.exists(status_path):
        with open(status_path) as f:
            return json.load(f)
    return {}


def analyze_validator_drift(matrix, validator_map, site_status):
    results = {}
    for site, data in matrix.get("sites", {}).items():
        plugins_present = set(data.get("plugins_used", []))
        validator_alerts = []

        for validator, vconf in validator_map.items():
            required_plugin = vconf.get("plugin")
            required = vconf.get("plugin_required", False)
            severity = vconf.get("on_plugin_removed", None)

            if required and required_plugin and severity:
                if required_plugin not in plugins_present:
                    validator_alerts.append(
                        {
                            "validator": validator,
                            "missing_plugin": required_plugin,
                            "severity": severity,
                            "description": vconf.get("tooltip", ""),
                        }
                    )

        drift_meta = site_status.get(site, {})
        drift_flag = drift_meta.get("validator_drift", False)
        site_health = drift_meta.get("site_health", "ok")
        suppression = drift_meta.get("score_suppression_reason", "")

        results[site] = {
            "alerts": validator_alerts,
            "drift": drift_flag,
            "health": site_health,
            "suppression_reason": suppression,
        }
    return results


def export_html(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    html = ["<html><head><title>Validator Drift Overlay</title></head><body>"]
    html.append("<h1>⚠️ Validator Plugin Drift (Phase 25d)</h1>")

    for site, result in results.items():
        color = BADGE_COLORS.get(result["health"], "#999")
        badge = f"<span style='background:{color};padding:4px;border-radius:4px;color:white;'>{result['health'].upper()}</span>"
        html.append(f"<h2>{site} {badge}</h2><ul>")

        for alert in result["alerts"]:
            icon = VALIDATOR_DRIFT_BADGES.get(alert["severity"], {}).get("icon", "❔")
            tip = alert.get("description") or VALIDATOR_DRIFT_BADGES.get(alert["severity"], {}).get("tooltip", "")
            html.append(
                f"<li title='{tip}'>{icon} <b>{alert['validator']}</b> → "
                f"<code>{alert['missing_plugin']}</code> "
                f"[{alert['severity'].upper()}]</li>"
            )

        if result.get("suppression_reason"):
            html.append(f"<li><i>💤 Score suppressed: {result['suppression_reason']}</i></li>")

        html.append("</ul>")
    html.append("</body></html>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[✓] Drift overlay exported to HTML → {path}")


def export_json(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Drift overlay exported to JSON → {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze validator-plugin drift with suppression logic")
    parser.add_argument("--matrix-path", default="output/schema_matrix.json")
    parser.add_argument("--yaml-path", default="validation_matrix.yaml")
    parser.add_argument("--status-path", default="output/output_status.json")
    parser.add_argument("--output-json", default="output/validator_drift_overlay.json")
    parser.add_argument("--output-html", default="output/validator_drift_overlay.html")
    args = parser.parse_args()

    matrix = load_matrix(args.matrix_path)
    validator_map = load_validation_yaml(args.yaml_path)
    status = load_status_json(args.status_path)
    results = analyze_validator_drift(matrix, validator_map, status)
    export_json(results, args.output_json)
    export_html(results, args.output_html)


if __name__ == "__main__":
    main()
