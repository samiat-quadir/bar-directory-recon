# === run_phase_21b_analysis.py ===

import os
import json

LATEST_MATRIX = "output/schema_matrix.json"
ARCHIVE_DIR = "output/archive"

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"[✗] Missing: {path}")
        return False
    print(f"[✓] Found: {path}")
    return True

def get_sites_from_matrix(path):
    with open(path) as f:
        matrix = json.load(f)
    return list(matrix.get("sites", {}).keys())

def main():
    print("📊 Phase 21b Analysis Orchestrator Started\n")
    all_clear = True

    if not check_file_exists(LATEST_MATRIX):
        all_clear = False

    for fname in os.listdir(ARCHIVE_DIR):
        if fname.endswith(".json") and "schema_matrix" in fname:
            check_file_exists(os.path.join(ARCHIVE_DIR, fname))

    if all_clear:
        sites = get_sites_from_matrix(LATEST_MATRIX)
        print(f"\n[✓] Sites in matrix: {sites}")
        print("[✓] Phase 21b checks complete.\n")
        exit(0)
    else:
        print("[✗] One or more required files missing.")
        exit(1)

if __name__ == "__main__":
    main()
