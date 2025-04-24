# === universal_recon/utils/module_health_checker.py ===

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import importlib
import json
import argparse
from pathlib import Path

REQUIRED_IMPORTS = [
    "universal_recon.plugin_aggregator",
    "universal_recon.analytics.schema_matrix_collector",
    "universal_recon.analytics.score_drift_export",
    "universal_recon.analytics.validator_drift_overlay",
    "universal_recon.utils.status_summary_emitter",
    "universal_recon.validators.validation_matrix"
]

REQUIRED_FILES = [
    "output/schema_matrix.json",
    "validators/validation_matrix.yaml"
]


CHECKS = []

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        CHECKS.append(("IMPORT", module_name, "✅"))
    except Exception as e:
        CHECKS.append(("IMPORT", module_name, f"❌ {e}"))

def check_file(path):
    if os.path.exists(path):
        CHECKS.append(("FILE", path, "✅"))
    else:
        CHECKS.append(("FILE", path, "❌ Missing"))

def check_schema_matrix(path):
    if not os.path.exists(path):
        return CHECKS.append(("SCHEMA", path, "❌ File Missing"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data.get("sites"):
            return CHECKS.append(("SCHEMA", path, "❌ No 'sites' key in JSON"))
        CHECKS.append(("SCHEMA", path, "✅ JSON OK"))
    except Exception as e:
        CHECKS.append(("SCHEMA", path, f"❌ Invalid JSON: {e}"))


def run_diagnostics():
    print("\n🩺 MODULE HEALTH CHECK SUMMARY:\n")
    for check_type, target, result in CHECKS:
        print(f"[{check_type}] {target} → {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run module diagnostics")
    parser.add_argument("--site", help="Site name (optional)", required=False)
    args = parser.parse_args()

    print("Running diagnostics for Universal Recon module...\n")

    for mod in REQUIRED_IMPORTS:
        check_import(mod)

    for file in REQUIRED_FILES:
        check_file(file)

    check_schema_matrix("output/schema_matrix.json")

    run_diagnostics()

    print("\n✅ Diagnostics complete.")
