# === validators/validator_drift_overlay.py ===

import json
import yaml
import os

BADGE_COLORS = {
    "critical": "#e74c3c",
    "warning": "#f1c40f",
    "info": "#3498db"
}

def load_matrix(matrix_path):
    with open(matrix_path) as f:
        return json.load(f)

def load_validation_yaml(yaml_path=None):
    if not yaml_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(script_dir, "..", "validation_matrix.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def analyze_validator_drift(matrix, validator_map):
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
                    validator_alerts.append({
                        "validator": validator,
                        "missing_plugin": required_plugin,
                        "severity": severity
                    })

        if validator_alerts:
            results[site] = validator_alerts
    return results

def export_json(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Drift overlay exported to JSON → {path}")

def export_html(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    html = ["<html><head><title>Validator Drift Overlay</title></head><body>"]
    html.append("<h1>⚠️ Validator Plugin Drift</h1>")

    for site, alerts in results.items():
        html.append(f"<h2>{site}</h2><ul>")
        for alert in alerts:
            color = BADGE_COLORS.get(alert["severity"], "#999")
            html.append(
                f"<li><span style='background:{color};padding:3px;border-radius:3px;color:white;'>"
                f"{alert['severity'].upper()}</span> "
                f"<b>{alert['validator']}</b> requires missing plugin "
                f"<code>{alert['missing_plugin']}</code></li>"
            )
        html.append("</ul>")
    html.append("</body></html>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[✓] Drift overlay exported to HTML → {path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze validator-plugin drift")
    parser.add_argument("--matrix-path", default="output/schema_matrix.json", help="Path to schema_matrix.json")
    parser.add_argument("--yaml-path", default="universal_recon/validators/validation_matrix.yaml", help="Path to validator config YAML")
    parser.add_argument("--output-json", default="output/validator_drift_overlay.json", help="Where to write JSON results")
    parser.add_argument("--output-html", default="output/validator_drift_overlay.html", help="Where to write HTML overlay")
    args = parser.parse_args()

    matrix = load_matrix(args.matrix_path)
    validator_map = load_validation_yaml(args.yaml_path)
    results = analyze_validator_drift(matrix, validator_map)

    if not results:
        print("✅ No validator drift detected. All required plugins are present.")
    else:
        export_json(results, args.output_json)
        export_html(results, args.output_html)

if __name__ == "__main__":
    main()
