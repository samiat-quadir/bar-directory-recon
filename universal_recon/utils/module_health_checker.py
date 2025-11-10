# universal_recon/utils/module_health_checker.py

import importlib
import importlib.util
import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HTML_PATH = "output/module_health_report.html"


MODULES_TO_CHECK = {
    "universal_recon.plugin_loader": None,
    "universal_recon.plugin_aggregator": None,
    "universal_recon.analytics.schema_matrix_collector": ["collect_schema_matrix"],
    "universal_recon.analytics.schema_score_linter": ["run_schema_score_lint"],
    "universal_recon.analytics.validator_drift_overlay": ["main"],
    "universal_recon.utils.status_summary_emitter": ["emit_status"],
    "universal_recon.validators.validation_matrix": ["load_validation_matrix"],
}

FILES_TO_CHECK = [
    "output/schema_matrix.json",
    "universal_recon/validators/validation_matrix.yaml",
    "output/fieldmap/utah_bar_fieldmap.json",  # Add a sample fieldmap for staleness check
]

STALE_THRESHOLD_HOURS = 24


def check_import_and_functions(module_path, functions):
    try:
        module = importlib.import_module(module_path)
        if functions:
            missing = [f for f in functions if not hasattr(module, f)]
            return (True, missing)
        return (True, [])
    except Exception:
        return (False, [])


def check_staleness(path):
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    age_hours = (time.time() - mtime) / 3600
    return age_hours


def build_html_report(
    results, file_results, staleness_warnings, missing_matrix, html_path
):
    rows = []
    for mod, (status, missing_funcs) in results.items():
        emoji = "✅" if status and not missing_funcs else "❌"
        color = "#2ecc71" if status and not missing_funcs else "#e74c3c"
        fn_text = (
            "All OK" if not missing_funcs else f"Missing: {', '.join(missing_funcs)}"
        )
        rows.append(
            f"<tr><td>{mod}</td><td style='color:{color}'>{emoji}</td><td>{fn_text}</td></tr>"
        )
    for path, exists in file_results.items():
        emoji = "✅" if exists else "❌"
        color = "#2ecc71" if exists else "#e67e22"
        status = "Exists" if exists else "Missing"
        rows.append(
            f"<tr><td>{path}</td><td style='color:{color}'>{emoji}</td>"
            f"<td>{status}</td></tr>"
        )
    for warning in staleness_warnings:
        rows.append(
            f"<tr><td colspan='3' style='color:#f39c12'><b>⚠️ {warning}</b></td></tr>"
        )
    if missing_matrix:
        rows.append(
            "<tr><td colspan='3' style='color:#e74c3c'>"
            "<b>❌ schema_matrix.json missing. Suggest re-running main.py</b>"
            "</td></tr>"
        )
    html = f"""
    <html>
    <head>
        <title>Universal Recon — Module Health Report</title>
        <style>
            body {{ font-family: sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
            th {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>🩺 Universal Recon — Module Health Checker</h2>
        <table>
            <tr><th>Component</th><th>Status</th><th>Details</th></tr>
            {''.join(rows)}
        </table>
    </body>
    </html>
    """
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] HTML report written to {html_path}")


def main():
    print("Running diagnostics for Universal Recon module...\n")
    results = {}
    for mod, funcs in MODULES_TO_CHECK.items():
        status, missing_funcs = check_import_and_functions(mod, funcs)
        results[mod] = (status, missing_funcs)
        emoji = "✅" if status and not missing_funcs else "❌"
        print(
            f"{emoji} {mod}"
            + (f" — Missing: {', '.join(missing_funcs)}" if missing_funcs else "")
        )
    file_results = {}
    staleness_warnings = []
    missing_matrix = False
    for path in FILES_TO_CHECK:
        exists = os.path.exists(path)
        file_results[path] = exists
        emoji = "✅" if exists else "❌"
        print(f"{emoji} {path}")
        if exists:
            age = check_staleness(path)
            if age is not None and age > STALE_THRESHOLD_HOURS:
                warning = f"{path} is stale (older than {STALE_THRESHOLD_HOURS}h, age: {age:.1f}h)"
                staleness_warnings.append(warning)
                print(f"⚠️  {warning}")
        else:
            if path.endswith("schema_matrix.json"):
                missing_matrix = True
    build_html_report(
        results, file_results, staleness_warnings, missing_matrix, HTML_PATH
    )
    print("\n✅ Diagnostics complete.")


if __name__ == "__main__":
    main()
