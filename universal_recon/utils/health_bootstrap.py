# universal_recon/utils/health_bootstrap.py

import os
import sys
import importlib.util
from pathlib import Path

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
        print("⚠️  'universal_recon' folder not visible from CWD — check where you're running this from.")

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

if __name__ == "__main__":
    run_all_checks()
