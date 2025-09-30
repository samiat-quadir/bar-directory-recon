# universal_recon/utils/health_bootstrap.py

import importlib.util
import os
import sys
from pathlib import Path

# Ensure the project root (parent of universal_recon) is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, "../..")))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def banner(title):
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def check_sys_path():
    banner("PYTHONPATH + sys.path Check")
    print("[•] Current Working Directory:")
    print(f"    {os.getcwd()}")
    print("\n[•] sys.path entries:")
    for p in sys.path:
        print(f"    - {p}")
    if "universal_recon" not in os.listdir():
        print(
            "⚠️  'universal_recon' folder not visible from CWD — check where you're running this from."
        )


def insert_root_to_syspath():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    print(f"\n✅ Added root to sys.path → {root}")


def try_import(name):
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            print(f"❌ {name} → Module NOT found.")
        else:
            print(f"✅ {name} → Importable.")
    except Exception as e:
        print(f"❌ {name} → Failed: {e}")


def check_overlay_status(module_name, html_path):
    print(f"\n--- Overlay Check: {module_name} ---")
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ {module_name} → Module NOT found. [BADGE: MISSING]")
            return
        print(f"✅ {module_name} → Importable.")
        if os.path.exists(html_path):
            print(f"[BADGE: OK] {html_path} exists.")
        else:
            print(f"[BADGE: NEEDS REGENERATION] {html_path} missing.")
    except Exception as e:
        print(f"❌ {module_name} → Failed: {e} [BADGE: MISSING]")


def run_all_checks():
    check_sys_path()
    insert_root_to_syspath()
    banner("MODULE IMPORT CHECKS")
    modules = [
        "universal_recon.plugin_loader",
        "universal_recon.plugin_aggregator",
        "universal_recon.analytics.schema_matrix_collector",
        "universal_recon.analytics.score_drift_export",
        "universal_recon.analytics.validator_drift_overlay",
        "universal_recon.utils.status_summary_emitter",
        "universal_recon.validators.validation_matrix",
        "universal_recon.core.report_printer",
    ]
    for mod in modules:
        try_import(mod)
    # Overlay awareness
    check_overlay_status(
        "universal_recon.analytics.plugin_decay_overlay",
        "output/plugin_decay_overlay.html",
    )
    check_overlay_status(
        "universal_recon.analytics.validator_drift_overlay",
        "output/validator_drift_overlay.html",
    )


if __name__ == "__main__":
    run_all_checks()
