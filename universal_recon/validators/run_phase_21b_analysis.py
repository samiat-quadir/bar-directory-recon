# === universal_recon/validators/run_phase_21b_analysis.py ===

import json
import os

MATRIX_PATH = "output/schema_matrix.json"
STATUS_PATH = "output/output_status.json"


def validate_matrix_structure(matrix):
    if "sites" not in matrix:
        print("❌ Matrix missing 'sites' key.")
        return False

    any_site_fail = False
    for site, data in matrix["sites"].items():
        if "score_summary" not in data:
            print(f"❌ {site}: missing score_summary")
            any_site_fail = True
        if "plugins_used" not in data:
            print(f"❌ {site}: missing plugins_used")
            any_site_fail = True
        if "anomaly_flags" not in data:
            print(f"⚠️  {site}: no anomaly_flags present")

    return not any_site_fail


def validate_site_status():
    if not os.path.exists(STATUS_PATH):
        print("⚠️  No status summary found (skipping validator_drift check)")
        return True

    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        status = json.load(f)

    issue_found = False
    for site, info in status.items():
        if info.get("site_health") == "degraded":
            print(
                f"🟥 {site}: DEGRADATION DETECTED → Plugins Removed: {info.get('plugins_removed', [])}"
            )
            issue_found = True
        elif info.get("validator_drift"):
            print(f"🟧 {site}: validator_drift = True")

    return not issue_found


def run_sanity_check():
    if not os.path.exists(MATRIX_PATH):
        print("❌ schema_matrix.json is missing.")
        return False

    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        matrix = json.load(f)

    print("\n🔍 Validating schema_matrix.json structure...")
    structure_ok = validate_matrix_structure(matrix)

    print("\n🔍 Validating site validator drift status...")
    status_ok = validate_site_status()

    if structure_ok and status_ok:
        print("\n✅ Phase 21b–25c Sanity Check Passed.")
        return True
    else:
        print("\n❌ Issues found during sanity check.")
        return False


if __name__ == "__main__":
    run_sanity_check()
