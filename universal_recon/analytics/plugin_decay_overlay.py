# universal_recon/analytics/plugin_decay_overlay.py

import json, os, argparse, yaml

STATUS_PATH = "output/output_status.json"
MATRIX_PATH = "output/schema_matrix.json"
YAML_PATH = "universal_recon/validators/validation_matrix.yaml"
EXPORT_HTML = "output/plugin_decay_overlay.html"
EXPORT_JSON = "output/plugin_decay_overlay.json"

BADGE_COLORS = {
    "critical": "#e74c3c",
    "warning": "#f1c40f",
    "info": "#3498db",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_overlay():
    if not os.path.exists(MATRIX_PATH):
        print("❌ Matrix missing.")
        return

    matrix = load_json(MATRIX_PATH)
    status = load_json(STATUS_PATH) if os.path.exists(STATUS_PATH) else {}
    valmap = load_yaml(YAML_PATH)

    output = {}
    for site, data in matrix.get("sites", {}).items():
        used_plugins = set(data.get("plugins_used", []))
        plugin_risks = []

        for validator, vconf in valmap.items():
            plugin = vconf.get("plugin")
            if not plugin or plugin in used_plugins:
                continue
            plugin_risks.append(
                {
                    "plugin": plugin,
                    "validator": validator,
                    "severity": vconf.get("on_plugin_removed", "info"),
                    "penalty": vconf.get("drift_penalty", 0.0),
                    "tooltip": vconf.get("tooltip", ""),
                }
            )

        site_status = status.get(site, {})
        output[site] = {
            "site_health": site_status.get("site_health", "ok"),
            "score_suppressed_by": site_status.get("score_suppressed_by", 0),
            "plugins_removed": site_status.get("plugins_removed", []),
            "validator_risk": plugin_risks,
        }

    with open(EXPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        print(f"[✓] Exported plugin decay risk JSON → {EXPORT_JSON}")

    # Build HTML
    html = [
        "<html><head><title>Plugin Decay Overlay</title></head><body><h1>Plugin Risk Overlay</h1>"
    ]
    for site, meta in output.items():
        html.append(f"<h2>{site} – Health: {meta['site_health'].upper()}</h2><ul>")
        for risk in meta["validator_risk"]:
            color = BADGE_COLORS.get(risk["severity"], "#ccc")
            html.append(
                f"<li><span style='background:{color};padding:2px;border-radius:3px;color:white;'>"
                f"{risk['severity'].upper()}</span> "
                f"Missing <b>{risk['plugin']}</b> (used by validator <i>{risk['validator']}</i>) "
                f"→ Penalty: {risk['penalty'] * 100:.0f}% "
                f"<small>🛈 {risk['tooltip']}</small></li>"
            )
        html.append("</ul>")
        if meta["score_suppressed_by"]:
            html.append(f"<p><b>⚠️ Score suppressed: −{meta['score_suppressed_by']}%</b></p>")
    html.append("</body></html>")

    with open(EXPORT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
        print(f"[✓] Exported plugin decay overlay HTML → {EXPORT_HTML}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", default=MATRIX_PATH)
    parser.add_argument("--status", default=STATUS_PATH)
    parser.add_argument("--yaml", default=YAML_PATH)
    args = parser.parse_args()
    generate_overlay()


if __name__ == "__main__":
    main()
