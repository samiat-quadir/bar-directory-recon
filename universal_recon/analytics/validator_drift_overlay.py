# === analytics/validator_drift_overlay.py ===

import json
import sys
from pathlib import Path

# ✅ Always fix: Ensure `utils/` is importable from universal_recon root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.validator_drift_badges import VALIDATOR_DRIFT_BADGES
from utils.snapshot_manager import fallback_latest_matrix_path
from utils.validation_loader import load_validation_matrix

DEFAULT_MATRIX_PATH = "output/schema_matrix.json"
OUTPUT_PATH = "output/validator_drift_overlay.html"


def load_matrix(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Matrix file not found at {path}")
        return None


def build_html_overlay(matrix, validator_map):
    if not matrix or "sites" not in matrix:
        return "<p>No valid schema matrix found.</p>"

    rows = []
    for site, site_data in matrix["sites"].items():
        plugins = site_data.get("plugins_used", [])
        risk_rows = []

        for validator, info in validator_map.items():
            plugin = info.get("linked_plugin")
            required = info.get("plugin_required", False)
            severity = info.get("on_plugin_removed", "info")

            if plugin and required and plugin not in plugins:
                badge = VALIDATOR_DRIFT_BADGES.get(severity, VALIDATOR_DRIFT_BADGES["info"])
                risk_rows.append(
                    f"<tr><td>{validator}</td><td>{plugin}</td>"
                    f"<td class='{badge['css_class']}' title='{badge['tooltip']}'>{badge['icon']} {severity}</td></tr>"
                )

        table = (
            f"<h3>{site}</h3>"
            f"<table><tr><th>Validator</th><th>Missing Plugin</th><th>Severity</th></tr>"
            + "\n".join(risk_rows)
            + "</table><hr>"
            if risk_rows else f"<h3>{site}</h3><p>✅ No validator-linked plugin drift.</p><hr>"
        )
        rows.append(table)

    return f"""
    <html><head><style>
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    .validator-critical {{ background: #f8d7da; color: #721c24; }}
    .validator-warning  {{ background: #fff3cd; color: #856404; }}
    .validator-info     {{ background: #d1ecf1; color: #0c5460; }}
    </style></head><body>
    <h2>🧩 Validator Drift Overlay</h2>
    {''.join(rows)}
    </body></html>
    """


def main():
    matrix_path = Path(DEFAULT_MATRIX_PATH)
    if not matrix_path.exists():
        fallback = fallback_latest_matrix_path()
        if fallback:
            print(f"⚠️  Falling back to: {fallback}")
            matrix_path = Path(fallback)
        else:
            print("❌ No schema matrix available.")
            return

    matrix = load_matrix(matrix_path)
    validator_map = load_validation_matrix()
    html = build_html_overlay(matrix, validator_map)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] Validator drift overlay written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
